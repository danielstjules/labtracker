from django.test import TestCase, LiveServerTestCase
from labtracker.models import Item, Request, Download, Comment
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

    def tearDown(self):
        self.selenium.delete_all_cookies()

    def link_text_exists(self, link_text):
        try:
            self.selenium.find_element_by_link_text(link_text)
        except NoSuchElementException:
            return False
        return True

    def xpath_exists(self, xpath):
        try:
            self.selenium.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True

    def element_with_selector_exists(self, selector):
        try:
            self.selenium.find_element_by_css_selector(selector)
        except NoSuchElementException:
            return False
        return True

    def text_exists(self, text, xpath="//body"):
        try:
            element = self.selenium.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False

        if text in element.text:
            return True
        else:
            return False

    def login(self, username, password):
        # Go to the login page and try logging in with the provided credentials
        self.selenium.get('%s' % self.live_server_url)
        self.selenium.find_element_by_link_text('Log in').click()
        username_input = self.selenium.find_element_by_name('username')
        username_input.send_keys(username)
        password_input = self.selenium.find_element_by_name('password')
        password_input.send_keys(password)
        self.selenium.find_element_by_class_name('submit').click()

    def create_items_and_requests(self, x):
        # Creates x number of items and requests
        for i in xrange(x):
            self.item = G(Item)
            self.request = G(Request, item=self.item)

    def create_generic_item(self):
        # Quick helper in the absence of fixtures
        item = G(Item, local_num=9999, part_class='parts class',
                 location='cart 8', description='test item', cfi='never',
                 company='A Business', part_num='X9X9', serial_num='8A',
                 asset_num='sample_num', notes='Testing')
        return item


class LoginTests(SeleniumTests):
    """Tests the Login view and related template"""

    def test_valid_credentials(self):
        self.login(self.admin_name, self.admin_pass)
        self.assertTrue(self.link_text_exists('Logout'))

    def test_invalid_credentials(self):
        self.login(self.admin_name, 'wrong password')
        self.assertTrue(self.element_with_selector_exists('.error_message'))


class ItemListTests(SeleniumTests):
    """Tests the Item List (home page)"""

    def test_no_items(self):
        self.selenium.get('%s' % self.live_server_url)
        self.assertTrue(self.text_exists('No items'))

    def test_pagination_displays_pages(self):
        # Test that it contains a li in the pagination div with class active,
        # as well as anchors with the text 1 and 2
        self.create_items_and_requests(60)
        self.selenium.get('%s' % self.live_server_url)
        self.assertTrue(self.xpath_exists(
            "//div[contains(@class,'pagination')]/ul/li[@class='active']"))
        self.assertTrue(self.xpath_exists(
            "//div[contains(@class,'pagination')]/ul/li/a[text()='1']"))
        self.assertTrue(self.xpath_exists(
            "//div[contains(@class,'pagination')]/ul/li/a[text()='2']"))

    def test_secondary_pages_contain_items(self):
        # Go to the 2nd, then 3rd page and check that the equipment_list contains
        # an anchor
        self.create_items_and_requests(110)
        self.selenium.get('%s' % self.live_server_url)
        page_two = self.selenium.find_element_by_xpath(
            "//div[contains(@class,'pagination')]/ul/li/a[text()='2']")
        page_two.click()
        page_three = self.selenium.find_element_by_xpath(
            "//div[contains(@class,'pagination')]/ul/li/a[text()='3']")
        page_three.click()
        self.assertTrue(self.xpath_exists(
            "//table[@id='equipment_list']/tbody/tr/td/a"))

    def test_table_links_to_items(self):
        # Make sure the table contains anchors with the item's absolute url
        self.create_items_and_requests(1)
        self.selenium.get('%s' % self.live_server_url)
        item = Item.objects.order_by('id')[0]
        table = "//table[@id='equipment_list']"
        item_xpath = "%s/tbody/tr/td/a[@href='%s']" % (table, item.get_absolute_url())
        self.assertTrue(self.xpath_exists(item_xpath))

    def test_table_in_asc_order_of_local_num(self):
        # Equipment should be displayed in ascending order by local_num (#)
        self.create_items_and_requests(5)
        self.selenium.get('%s' % self.live_server_url)
        items = Item.objects.order_by('local_num')[:5]
        for i in xrange(5):
            item = items[i]
            row = "//table[@id='equipment_list']/tbody/tr[%i]/td/" % (i + 1)
            item_xpath = "%sa[@href='%s']" % (row, item.get_absolute_url())
            self.assertTrue(self.xpath_exists(item_xpath))

    def test_displays_necessary_fields(self):
        # Item list should show local_num (#), part_class, location, description,
        # cfi, company and part_num
        item = G(Item, local_num='9009', part_class='parts class',
                 location='cart 10', description='test item', cfi='never',
                 company='A Business', part_num='X9999999')
        self.selenium.get('%s' % self.live_server_url)
        fieldValues = [item.local_num, item.part_class, item.location,
                       item.description, item.cfi, item.company, item.part_num]
        table = "//table[@id='equipment_list']"
        for value in fieldValues:
            self.assertTrue(self.text_exists(value, table))


class ItemDetailTests(SeleniumTests):
    """Tests the item_detail view and template"""

    def test_shows_all_available_fields(self):
        # Test that all fields are displayed on the details page
        item = self.create_generic_item()
        self.selenium.get('%s/item/%i/' % (self.live_server_url, item.pk))
        fieldValues = [item.local_num, item.part_class, item.location,
                       item.description, item.cfi, item.company, item.part_num,
                       item.serial_num, item.asset_num, item.notes, 1]
        for value in fieldValues:
            self.assertTrue(self.text_exists(str(value)))

    def test_request_use_form_visibility_when_logged_out(self):
        # Make sure the form isn't visible when not logged in
        item = self.create_generic_item()
        self.selenium.get('%s/item/%i/' % (self.live_server_url, item.pk))
        self.assertFalse(self.xpath_exists("//form"))

    def test_request_use_form_visibility_when_logged_in(self):
        # Make sure the form is visible when logged in
        item = self.create_generic_item()
        self.login(self.user_name, self.user_pass)
        self.selenium.get('%s/item/%i/' % (self.live_server_url, item.pk))
        self.assertTrue(self.xpath_exists("//form"))

    def test_listing_downloads(self):
        # Downloads and their information should be available
        item = self.create_generic_item()
        downloads = []
        for i in xrange(5):
            downloads.append(G(Download, item=item))

        self.selenium.get('%s/item/%i/' % (self.live_server_url, item.pk))
        for i in xrange(5):
            self.assertTrue(self.text_exists(downloads[i].name))
            self.assertTrue(self.text_exists(downloads[i].notes))

    def test_listing_requests(self):
        # Related requests should be listed
        item = self.create_generic_item()
        requests = []
        for i in xrange(5):
            requests.append(G(Request, item=item))

        self.selenium.get('%s/item/%i/' % (self.live_server_url, item.pk))
        for i in xrange(5):
            self.assertTrue(self.text_exists(requests[i].__unicode__()))

    def test_incrementing_views(self):
        # Test that item.view increments with each request
        item = self.create_generic_item()
        self.selenium.get('%s/item/%i/' % (self.live_server_url, item.pk))
        for i in xrange(5):
            self.selenium.refresh()
        self.assertTrue(self.text_exists('6'))


class SubmitRequestTests(SeleniumTests):
    """Tests the submit_request view and the template it renders"""

    def submit_request(self, notes):
        # Submits and item request
        notes_input = self.selenium.find_element_by_name('notes')
        notes_input.send_keys(notes)
        self.selenium.find_element_by_xpath("//form/input[@type='submit']").click()

    def test_request_fail_if_not_logged_in(self):
        # Delete session id cookie to try submitting when not logged in
        item = self.create_generic_item()
        self.login(self.user_name, self.user_pass)
        self.selenium.get('%s/item/%i/' % (self.live_server_url, item.pk))
        self.selenium.delete_cookie('sessionid')
        notes = 'Test request note'
        self.submit_request(notes)
        self.assertEqual(Request.objects.filter(notes=notes).count(), 0)
        self.assertTrue(self.element_with_selector_exists('.error_message'))

    def test_request_pass_if_logged_in(self):
        item = self.create_generic_item()
        self.login(self.user_name, self.user_pass)
        self.selenium.get('%s/item/%i/' % (self.live_server_url, item.pk))
        notes = 'Test request notes'
        self.submit_request(notes)
        self.assertEqual(Request.objects.filter(notes=notes).count(), 1)
        self.assertTrue(self.element_with_selector_exists('.success_message'))


class ModifyRequestStatusTests(SeleniumTests):
    """Tests modify_request_status view"""

    def test_changing_status_to_valid_choice(self):
        # Tests switching to all of STATUS_CHOICES
        self.create_items_and_requests(1)
        self.login(self.admin_name, self.admin_pass)
        request = Request.objects.get(pk=1)

        for key, val in request.STATUS_CHOICES:
            self.selenium.get('%s/request/1/' % self.live_server_url)
            # Click on select box
            self.selenium.find_element_by_name('choice').click()
            # Click on option
            option = "//select[@id='choice']/option[@value='%s']" % key
            self.selenium.find_element_by_xpath(option).click()

            # After redirect, check that the value is now selected
            self.selenium.find_element_by_name('choice').click()
            selected = "//option[@value='%s' and @class='selected']" % key
            self.assertTrue(self.xpath_exists(selected))
            request = Request.objects.get(pk=1)
            self.assertTrue(request.status, key)

    def test_should_fail_if_logged_out(self):
        self.create_items_and_requests(1)
        self.login(self.admin_name, self.admin_pass)
        self.selenium.get('%s/request/1/' % self.live_server_url)
        # Delete sessionid cookie to logout
        self.selenium.delete_cookie('sessionid')

        # Click on select box
        self.selenium.find_element_by_name('choice').click()
        # Click on Completed option
        completed_option = "//select[@id='choice']/option[@value='Completed']"
        self.selenium.find_element_by_xpath(completed_option).click()

        # Status should still be pending, rather than completed
        request = Request.objects.get(pk=1)
        self.assertTrue(request.status, request.PENDING)


class PostCommentTests(SeleniumTests):
    """Tests the post_comment view"""

    def test_fail_if_logged_out(self):
        self.create_items_and_requests(1)
        self.login(self.admin_name, self.admin_pass)
        self.selenium.get('%s/request/1/' % self.live_server_url)
        # Delete sessionid cookie to logout
        self.selenium.delete_cookie('sessionid')

        # Submit comment
        comment_textarea = self.selenium.find_element_by_id('comment')
        content = 'Testing'
        comment_textarea.send_keys(content)
        submit_path = "//form[@id='comment_form']/input[@type='submit']"
        self.selenium.find_element_by_xpath(submit_path).click()

        # Make sure the comment wasn't added
        self.assertTrue(self.element_with_selector_exists('.error_message'))
        self.assertEqual(Comment.objects.filter(content=content).count(), 0)

    def test_comment_if_logged_in(self):
        self.create_items_and_requests(1)
        self.login(self.admin_name, self.admin_pass)
        self.selenium.get('%s/request/1/' % self.live_server_url)

        # Submit comment
        comment_textarea = self.selenium.find_element_by_id('comment')
        content = 'Testing'
        comment_textarea.send_keys(content)
        submit_path = "//form[@id='comment_form']/input[@type='submit']"
        self.selenium.find_element_by_xpath(submit_path).click()

        self.selenium.get('%s/request/1/' % self.live_server_url)
        self.assertEqual(Comment.objects.filter(content=content).count(), 1)
        self.assertTrue(self.text_exists(content))


class RequestListTests(SeleniumTests):
    """Tests the request_list view"""

    def test_show_error_if_logged_out(self):
        self.selenium.get('%s/requests/' % self.live_server_url)
        self.assertTrue(self.element_with_selector_exists('.error_message'))

    def test_show_requests_with_status_and_links(self):
        # Generate two requests by the same user and check their requests page
        item = self.create_generic_item()
        user = User.objects.get(username=self.user_name)
        first_req = G(Request, item=item, user=user, status=Request.APPROVED)
        second_req = G(Request, item=item, user=user, status=Request.COMPLETED)
        self.login(self.user_name, self.user_pass)
        self.selenium.get('%s/requests/' % self.live_server_url)

        # Links to both requests should be present
        first_link = "//tbody/tr/td/a[@href='%s']" % first_req.get_absolute_url()
        self.assertTrue(self.xpath_exists(first_link))
        second_link = "//tbody/tr/td/a[@href='%s']" % second_req.get_absolute_url()
        self.assertTrue(self.xpath_exists(second_link))

        # The request statuses should be displayed
        self.assertTrue(self.text_exists(first_req.status, '//tbody'))
        self.assertTrue(self.text_exists(second_req.status, '//tbody'))


class RequestDetailTests(SeleniumTests):
    """Tests the request_detail view"""

    def test_displays_necessary_fields(self):
        # Test that user, item, notes and status are displayed
        item = self.create_generic_item()
        user = User.objects.get(username=self.user_name)
        notes = 'test request notes'
        req = G(Request, item=item, user=user, notes=notes)

        self.login(self.admin_name, self.admin_pass)
        self.selenium.get('%s/request/1/' % self.live_server_url)

        fieldValues = [item.description, req.status, user.username, notes]
        for value in fieldValues:
            self.assertTrue(self.text_exists(str(value)))

    def test_show_error_if_logged_out(self):
        self.create_items_and_requests(1)
        self.selenium.get('%s/request/1/' % self.live_server_url)
        self.assertTrue(self.element_with_selector_exists('.error_message'))

    def test_show_change_status_select_if_staff(self):
        self.create_items_and_requests(1)
        self.login(self.admin_name, self.admin_pass)
        self.selenium.get('%s/request/1/' % self.live_server_url)
        self.assertTrue(self.element_with_selector_exists('#choice'))

    def test_hide_change_status_select_if_normal_user(self):
        self.create_items_and_requests(1)
        self.login(self.user_name, self.user_pass)
        self.selenium.get('%s/request/1/' % self.live_server_url)
        self.assertFalse(self.element_with_selector_exists('#choice'))

    def test_show_comment_form(self):
        #Make sure the textarea and submit button are shown in the comment form
        self.create_items_and_requests(1)
        self.login(self.user_name, self.user_pass)
        self.selenium.get('%s/request/1/' % self.live_server_url)

        textarea_path = "//form[@id='comment_form']/textarea"
        self.assertTrue(self.xpath_exists(textarea_path))

        submit_path = "//form[@id='comment_form']/input[@type='submit']"
        self.assertTrue(self.xpath_exists(submit_path))

    def test_show_comments(self):
        # Create the item, request, and comment under a normal user
        item = self.create_generic_item()
        user = User.objects.get(username=self.user_name)
        req = G(Request, item=item, user=user)
        comment_one = G(Comment, request=req, user=user, content='Test comment')
        comment_two = G(Comment, request=req, user=user, content='another')

        self.login(self.admin_name, self.admin_pass)
        self.selenium.get('%s/request/1/' % self.live_server_url)

        # Verify that the comment is shown
        self.assertTrue(self.text_exists(comment_one.content))
        self.assertTrue(self.text_exists(comment_two.content))
