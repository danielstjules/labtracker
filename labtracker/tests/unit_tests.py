from django.utils import unittest
from labtracker.models import Item, Download, Request
from django_dynamic_fixture import G


class ItemTest(unittest.TestCase):
    def test_item_string(self):
        """Items should use their description for their human readable form"""
        item_description = 'test desc'
        item = G(Item, description=item_description)
        self.assertEqual(unicode(item), item.description)


class DownloadTest(unittest.TestCase):
    def setUp(self):
        item = G(Item)
        self.download_name = 'test download'
        self.download = G(Download, item=item, name=self.download_name,
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
        self.item = G(Item, description=self.item_description)
        self.request = G(Request, item=self.item, status=Request.PENDING)

    def test_request_string(self):
        """Requests should use status and item name for their readable form"""
        intended = '[' + self.request.status + '] ' + self.item_description
        self.assertEqual(unicode(self.request), intended)

    def test_status_readable(self):
        """The status field should offer human readable choices"""
        choices_dict = dict(Request.STATUS_CHOICES)
        self.assertEqual(choices_dict[Request.PENDING], 'Pending')
