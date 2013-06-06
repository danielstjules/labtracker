from django.test import TestCase, LiveServerTestCase
from labtracker.models import Item, Request
from django_dynamic_fixture import G
from django.contrib.auth.models import User
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException


class UrlTests(TestCase):
    """Tests that URL patterns in urls.py route to views and return HTTP 200"""

    @classmethod
    def setUpClass(self):
        # Creates enough requests and items to generate 2 pages for pagination.
        # Also creates two tests accounts: one admin and regular user.
        # If we were dealing with more data, we could use fixtures.
        for i in xrange(60):
            self.item = G(Item)
            self.request = G(Request, item=self.item)

        # Couldn't login with users created with django_dynamic_fixture's G()
        self.user_name = 'TestUser'
        self.user_pass = 'test'
        User.objects.create_user(self.user_name, '', self.user_pass).save()

        self.admin_name = 'AdministrativeUser'
        self.admin_pass = 'test'
        User.objects.create_superuser(self.admin_name, '', self.admin_pass).save()

    def tearDown(self):
        # Don't forget to log out after each request
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
                                    {'notes': 'test'})
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


class SeleniumTests(LiveServerTestCase):
    """Base class for all Selenium test classes to inherit from"""

    @classmethod
    def setUpClass(self):
        self.selenium = WebDriver()
        self.selenium.implicitly_wait(3)
        super(SeleniumTests, self).setUpClass()

    @classmethod
    def tearDownClass(self):
        self.selenium.quit()
        super(SeleniumTests, self).tearDownClass()

    def setUp(self):
        # Create a test user and admin account
        self.user_name = 'SeleniumTestUser'
        self.user_pass = 'test'
        if User.objects.filter(username=self.user_name).count() == 0:
            User.objects.create_user(self.user_name, '', self.user_pass).save()

        self.admin_name = 'SeleniumAdministrativeUser'
        self.admin_pass = 'test'
        if User.objects.filter(username=self.admin_name).count() == 0:
            User.objects.create_superuser(self.admin_name, '', self.admin_pass).save()

    def link_text_exists(self, link_text):
        try:
            self.selenium.find_element_by_link_text(link_text)
        except NoSuchElementException:
            return False
        return True

    def element_with_selector_exists(self, selector):
        try:
            self.selenium.find_element_by_css_selector(selector)
        except NoSuchElementException:
            return False
        return True

    def login(self, username, password):
        # Go to the login page and try logging in with the provided credentials
        self.selenium.get('%s' % self.live_server_url)
        self.selenium.find_element_by_link_text('Log in').click()
        username_input = self.selenium.find_element_by_name('username')
        username_input.send_keys(username)
        password_input = self.selenium.find_element_by_name('password')
        password_input.send_keys(password)
        self.selenium.find_element_by_class_name('submit').click()


class LoginTests(SeleniumTests):
    """Tests the Login view and related template"""

    def test_login_with_valid_credentials(self):
        self.login(self.admin_name, self.admin_pass)
        self.assertTrue(self.link_text_exists('Logout'))
        self.selenium.delete_all_cookies()

    def test_login_with_invalid_credentials(self):
        self.login(self.admin_name, 'wrong password')
        self.assertTrue(self.element_with_selector_exists('.error_message'))
        self.selenium.delete_all_cookies()
