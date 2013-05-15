from django.test import TestCase
from labtracker.models import Item, Request
from django_dynamic_fixture import G
from django.contrib.auth.models import User


class UrlsTest(TestCase):
    """Test that URL patterns in urls.py route to views and return HTTP 200"""

    @classmethod
    def setUpClass(self):
        """Create enough requests and items to generate 2 pages for pagination.
        Also create two tests accounts: one admin and regular user.
        If we were dealing with more data, we could use fixtures."""
        for i in xrange(60):
            self.item = G(Item)
            self.request = G(Request, item=self.item)

        # Couldn't login with users created with django_dynamic_fixture's G()
        self.user_name = "TestUser"
        self.user_pass = "test"
        User.objects.create_user(self.user_name, '', self.user_pass).save()

        self.admin_name = "AdministrativeUser"
        self.admin_pass = "test"
        User.objects.create_superuser(self.admin_name, '', self.admin_pass).save()

    def tearDown(self):
        """Don't forget to log out after each request"""
        self.client.logout()

    def test_home_url(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_item_list_page_url(self):
        response = self.client.get('/2/')
        self.assertEqual(response.status_code, 200)

    def test_item_detail_url(self):
        response = self.client.get('/item/%i/' % self.item.pk)
        self.assertEqual(response.status_code, 200)

    def test_submit_request_url(self):
        self.client.login(username=self.user_name, password=self.user_pass)
        response = self.client.post('/item/%i/request/' % self.item.pk,
                                    {'notes': "test"})
        self.assertEqual(response.status_code, 200)

    def test_request_list_url(self):
        self.client.login(username=self.user_name, password=self.user_pass)
        response = self.client.get('/requests/')
        self.assertEqual(response.status_code, 200)

    def test_admin_request_list_url(self):
        self.client.login(username=self.admin_name, password=self.admin_pass)
        response = self.client.get('/requests_admin/')
        self.assertEqual(response.status_code, 200)

    def test_admin_request_list_page_url(self):
        self.client.login(username=self.admin_name, password=self.admin_pass)
        response = self.client.get('/requests_admin/2/')
        self.assertEqual(response.status_code, 200)

    def test_request_detail_url(self):
        self.client.login(username=self.admin_name, password=self.admin_pass)
        response = self.client.get('/request/%i/' % self.request.pk)
        self.assertEqual(response.status_code, 200)

    def test_modify_request_status_url(self):
        self.client.login(username=self.admin_name, password=self.admin_pass)
        response = self.client.post('/request/%i/modify/' % self.request.pk,
                                    {'choice': Request.APPROVED})
        self.assertEqual(response.status_code, 200)

    def test_login_url(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

    def test_logout_url(self):
        self.client.login(username=self.admin_name, password=self.admin_pass)
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 200)
