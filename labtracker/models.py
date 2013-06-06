from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from labtracker.excel_reports import ExcelReport
from django.core.files import File

import random
import os


class Item(models.Model):
    description = models.CharField(max_length=100)
    local_num = models.IntegerField()
    location = models.CharField(max_length=100, blank=True)
    cfi = models.CharField(max_length=20, blank=True)
    part_class = models.CharField(max_length=50, blank=True)
    company = models.CharField(max_length=100, blank=True)
    part_num = models.CharField(max_length=50, blank=True)
    serial_num = models.CharField(max_length=50, blank=True)
    asset_num = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    views = models.PositiveSmallIntegerField(default=0)

    def __unicode__(self):
        return u"%s" % self.description

    def get_absolute_url(self):
        return "/item/%i/" % self.pk

    def get_request_url(self):
        return "/item/%i/request/" % self.pk

    def get_admin_url(self):
        return "/admin/labtracker/item/%i/" % self.pk


class Download(models.Model):
    DTYPE_DATASHEET = 'D'
    DTYPE_MANUAL = 'M'
    DTYPE_SOFTWARE = 'S'
    DTYPE_OTHER = 'O'
    DTYPE_CHOICES = (
        (DTYPE_DATASHEET, 'Datasheet'),
        (DTYPE_MANUAL, 'Manual'),
        (DTYPE_SOFTWARE, 'Software'),
        (DTYPE_OTHER, 'Other'),
    )

    item = models.ForeignKey(Item)
    dtype = models.CharField(max_length=15, choices=DTYPE_CHOICES)
    name = models.CharField(max_length=250)
    url = models.URLField(blank=True)
    dfile = models.FileField(upload_to="download/%Y/%m")
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return u"%s" % self.name

    def get_filename(self):
        return self.dfile.__unicode__().rsplit('/', 1)[-1]


class Request(models.Model):
    PENDING = 'Pending'
    APPROVED = 'Approved'
    ACTIVE = 'Active'
    COMPLETED = 'Completed'
    DECLINED = 'Declined'
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (ACTIVE, 'Active'),
        (COMPLETED, 'Completed'),
        (DECLINED, 'Declined'),
    )

    item = models.ForeignKey(Item)
    user = models.ForeignKey(User, blank=True, null=True)
    read = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES,
                              default=PENDING)

    date_submitted = models.DateTimeField()
    date_updated = models.DateTimeField('last modified date')
    date_approved = models.DateTimeField(blank=True, null=True)
    date_active = models.DateTimeField('started use', blank=True, null=True)
    date_completed = models.DateTimeField('finished use', blank=True, null=True)
    date_declined = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return u"[%s] %s" % (self.status, str(self.item))

    def get_absolute_url(self):
        return "/request/%i/" % self.pk

    def get_modify_url(self):
        return "/request/%i/modify/" % self.pk

    def get_post_comment_url(self):
        return "/request/%i/post_comment/" % self.pk

    def save(self, *args, **kwargs):
        current_datetime = timezone.now()
        self.date_updated = current_datetime

        if self.pk is not None:
            # If there was an existing request, need to update its dates
            orig = Request.objects.get(pk=self.pk)

            # Change its read status for the admin
            if orig.read or not self.read:
                if self.date_submitted != self.date_updated:
                    self.read = False

            # Update the corresponding dates given a status change
            if orig.status != self.status:
                if self.status == 'approved':
                    self.date_approved = current_datetime
                elif self.status == 'active':
                    self.date_active = current_datetime
                elif self.status == 'completed':
                    self.date_completed = current_datetime
                elif self.status == 'declined':
                    self.date_declined = current_datetime

        else:
            # If this is a new request, then just set its submission date
            self.date_submitted = current_datetime
        super(Request, self).save(*args, **kwargs)

    def mark_read(self):
        self.read = True
        super(Request, self).save()

    def mark_unread(self):
        self.read = False
        super(Request, self).save()

    def is_open(self):
        if self.status == Request.COMPLETED or self.status == Request.DECLINED:
            return False
        return True


class Comment(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)
    request = models.ForeignKey(Request, blank=True, null=True)
    date_submitted = models.DateTimeField('submission date', auto_now_add=True)
    content = models.TextField(blank=True)

    def __unicode__(self):
        return self.id


class Report(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)
    description = models.TextField(blank=True)
    date_created = models.DateTimeField('creation date', auto_now_add=True)
    rfile = models.FileField(upload_to="report/%Y/%m", blank=True)

    def __unicode__(self):
        return u"%s" % self.url

    def get_delete_url(self):
        return "/report/%i/delete/" % self.pk

    def createExcelFile(self, start_date=None, end_date=None, company=None,
                        item_pk=None, title=None):
        """Creates and saves an excel workbook containing information on item
        requests within a specified range of dates. Can also limit the results
        to requests for a specific item, or items from a specific company."""
        requests = Request.objects.all()

        # Default to 'Report' if no title is provided
        title = 'Report' if title is None else title

        # Apply date range limits
        if start_date is not None:
            requests = Request.objects.exclude(date_submitted__lt=start_date)
        if end_date is not None:
            requests = requests.exclude(date_submitted__gt=end_date)

        # Filter by the item's company name if set
        if company is not None:
            requests = requests.filter(item__company=company)
        # Filter by the item's primary key if given
        if item_pk is not None:
            requests = requests.filter(item__pk=item_pk)

        # Order by item pk then submission date
        requests = requests.order_by('item__pk', 'date_submitted')

        # If there's no requests in the query set, return
        if len(requests) < 1:
            return

        # Otherwise create the workbook from those results
        report = ExcelReport(8)
        report.write_header(title)

        item = None
        for req in requests:
            # Because items are grouped by item, just compare the current & last
            # items. If they're different, add a new section head
            if item != req.item:
                item = req.item
                # Build section head from item's fields
                section_name = item.local_num + " - " + item.description
                if item.part_class:
                    section_name += " - " + item.part_class
                if item.company:
                    section_name += " - " + item.company
                if item.part_num:
                    section_name += " - " + item.part_num
                if item.serial_num:
                    section_name += " - " + item.serial_num
                if item.asset_num:
                    section_name += " - " + item.asset_num

                # Define a list of column names for the sub heading
                columns = ['User', 'Status', 'Applied', 'Approved', 'Declined',
                           'Use Start', 'Use End', 'Hours Used']

                report.write_section_head(section_name, columns)

            # Duration is the number of hours from date_active to date_completed
            # Represents how long the item was used
            duration = ""
            if req.date_completed and req.date_active:
                duration = req.date_completed - req.date_active
                duration = duration.hours

            # Add the request as an entry
            report.write_entry([
                req.user.__unicode__(),
                req.status,
                req.date_submitted,
                req.date_approved,
                req.date_declined,
                req.date_active,
                req.date_completed,
                duration
            ])

        # Save workbook to tmp file
        tmp_dir = 'tmp/'
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        file_name = hex(random.getrandbits(128))[2:-1] + ".xls"
        tmp_path = os.path.join('tmp/', file_name)
        report.save(tmp_path)

        # Save file to FileField, delete tmp file
        f = open(tmp_path, 'r')
        new_file = File(f)
        self.rfile.save(file_name, new_file)
        f.close()
        os.remove(tmp_path)
