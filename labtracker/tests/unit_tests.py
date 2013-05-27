from django.utils import unittest
from labtracker.models import Item, Download, Request
from django_dynamic_fixture import N
from datetime import timedelta
from django.utils import timezone


class ItemTest(unittest.TestCase):
    def test_item_string(self):
        """Items should use their description for their human readable form"""
        item_description = 'test desc'
        item = N(Item, description=item_description)
        self.assertEqual(unicode(item), item.description)


class DownloadTest(unittest.TestCase):
    def setUp(self):
        item = N(Item)
        self.download_name = 'test download'
        self.download = N(Download, item=item, name=self.download_name,
                          dtype=Download.DTYPE_DATASHEET)

    def test_item_string(self):
        """Downloads should use their name for their human readable form"""
        self.assertEqual(unicode(self.download), self.download_name)

    def test_dtype_readable(self):
        """The dtype field should offer human readable choices"""
        choices_dict = dict(Download.DTYPE_CHOICES)
        self.assertEqual(choices_dict[Download.DTYPE_DATASHEET], 'Datasheet')


class RequestTest(unittest.TestCase):
    def setUp(self):
        self.item_description = 'test desc'
        self.item = N(Item, description=self.item_description)

        self.request_completed = N(Request, item=self.item, status=Request.COMPLETED,
                                   date_submitted=timezone.now() - timedelta(days=6))
        self.request_declined = N(Request, item=self.item, status=Request.DECLINED,
                                  date_submitted=timezone.now() - timedelta(days=8))

    def test_request_string(self):
        """Requests should use status and item name for their readable form"""
        intended = '[' + self.request_completed.status + '] ' + self.item_description
        self.assertEqual(unicode(self.request_completed), intended)

    def test_status_readable(self):
        """The status field should offer human readable choices"""
        choices_dict = dict(Request.STATUS_CHOICES)
        self.assertEqual(choices_dict[Request.COMPLETED], 'Completed')

    def test_is_open_with_completed(self):
        """Completed requests should cause is_open to return False"""
        self.assertEqual(self.request_completed.is_open(), False)

    def test_is_open_with_declined(self):
        """Declined requests should cause is_open to return False"""
        self.assertEqual(self.request_declined.is_open(), False)

    def test_is_open_with_others(self):
        """is_open should return False for Pending, Approved, and Active"""
        open_statuses = [Request.PENDING, Request.APPROVED, Request.ACTIVE]
        for open_status in open_statuses:
            open_request = N(Request, item=self.item, status=open_status)
            self.assertEqual(open_request.is_open(), True)
