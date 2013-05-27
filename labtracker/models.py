from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Item(models.Model):
    description = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True)
    local_num = models.CharField(max_length=50, blank=True)
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
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return u"%s" % self.name


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
