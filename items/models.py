from django.db import models
import datetime
from django.utils import timezone

class Item(models.Model):
	location = models.CharField(max_length=100, blank=True)
	company = models.CharField(max_length=100, blank=True)
	local_num = models.CharField(max_length=50, blank=True)
	part_num = models.CharField(max_length=50, blank=True)
	serial_num = models.CharField(max_length=50, blank=True)
	asset_num = models.CharField(max_length=50, blank=True)
	description = models.TextField() # name/description
	notes = models.TextField(blank=True)
	views = models.PositiveSmallIntegerField(default=0)

	def __unicode__(self):
		return self.description

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
	STATUS_CHOICES = (
		('pending', 'Pending'),
		('approved', 'Approved'),
		('completed', 'Completed'),
		('declined', 'Declined'),
	)
	status = models.CharField(max_length=15, choices=STATUS_CHOICES)
	sub_date = models.DateTimeField('date submitted')
	app_date = models.DateTimeField('date approved', blank=True)
	comp_date = models.DateTimeField('date completed', blank=True)
	decl_date = models.DateTimeField('date declined', blank=True)
	notes = models.TextField()

	def __unicode__(self):
		return "[" + Item.objects.get(pk=item) + "] " + self.item

	def is_pending(self):
		return self.status == 'pending'

	def is_approved(self):
		return self.status == 'approved'

	def is_completed(self):
		return self.status == 'completed'

	def is_declined(self):
		return self.status == 'declined'

	def was_requested_recently(self):
		return self.sub_date >= timezone.now() - datetime.timedelta(days=1)