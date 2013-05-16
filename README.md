labtracker
===========

labtracker is a Django app developed at the request of [Dr. Ramon Maldonado-Basilio](<http://ptlab.site.uottawa.ca/dr-ramon-maldonado-basilio/>), a Post-Doctorial Researcher at the University of Ottawa. It has been designed to keep track of equipment information and use in a university lab setting. It was written by Vladimir Suse and myself in our free time.

![screenshot](http://danielstjules.com/labtracker/screenshot.gif)

Description
-----------

* Designed to be used on a private network, and requires that the admin generate all user accounts
* Items are requested for use by users, and the administration approve requests
* Requests can change between 5 statuses: Pending, Approved, Active (item in-use), Completed and Declined
* Timestamps for each status change are logged for future reports
* Both users and admin can comment on a request
* Users are notified of any changes to their request status, including new comments

Running Tests
-------------

Firstly, [django-dynamic-fixture](https://github.com/paulocheque/django-dynamic-fixture) is used to generate model instances for testing purposes. It can be installed by running:

	pip install django-dynamic-fixture

And [selenium](http://selenium-python.readthedocs.org/en/latest/) is used for functional tests. We use the FireFox WebDriver. Selenium can be installed using:

	pip install selenium

Then, to run the tests included in labtracker, simply navigate to the project folder and run:

	python manage.py test labtracker

Authors
-------

Application created by Daniel St. Jules, along with contributions from Vladimir Suse.

Licensing
---------

Licensed under the GPLv3. See LICENSE.txt for details.
