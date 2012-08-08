from django.db import models
import datetime
from django.utils import timezone
from django.contrib.auth.models import User

class Item(models.Model):
    name = models.CharField(max_length=50)
    location = models.CharField(max_length=100, blank=True)
    local_num = models.CharField(max_length=50, blank=True)
    company = models.CharField(max_length=100, blank=True)
    part_num = models.CharField(max_length=50, blank=True)
    serial_num = models.CharField(max_length=50, blank=True)
    asset_num = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    views = models.PositiveSmallIntegerField(default=0)

    def __unicode__(self):
        return self.name

class Download(models.Model):
    item = models.ForeignKey(Item)
    DTYPE_CHOICES = (
        ('datasheet', 'Datasheet'),
        ('manual', 'Manual'),
        ('software', 'Software'),
    )
    dtype = models.CharField(max_length=15, choices=DTYPE_CHOICES)
    name = models.CharField(max_length=250)
    url = models.URLField(blank=True)
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

class Request(models.Model):
    item = models.ForeignKey(Item)
    user = models.ForeignKey(User, blank=True, null=True)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('declined', 'Declined'),
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES)
    read = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    date_submitted = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField('last modified date', auto_now=True)
    date_approved = models.DateTimeField(blank=True, null=True)
    date_active = models.DateTimeField('started use', blank=True, null=True)
    date_completed = models.DateTimeField('finished use', blank=True, null=True)
    date_declined = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return "[" + self.status + "] " + str(self.item)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            orig = Request.objects.get(pk=self.pk)
            if not(orig.read == False and self.read == True):
                if self.date_submitted != self.date_updated:
                    self.read = False
        super(Request, self).save(*args, **kwargs)

    def mark_read(self):
        self.read = True
        super(Request, self).save()

    def was_submitted_recently(self):
        return self.date_submitted >= timezone.now() - datetime.timedelta(days=1)
    was_submitted_recently.admin_order_field = 'submitted'
    was_submitted_recently.boolean = True
    was_submitted_recently.short_description = 'Submitted Recently?'