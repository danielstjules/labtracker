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

Development Env Setup
---------------------

The following brief instructions assume that git, python, MySQL, [pip](http://www.pip-installer.org/en/latest/) and [virtualenv](https://pypi.python.org/pypi/virtualenv) are installed. Note that these instructions are not intended for a production environment. Consider using Apache with mod_python, or Gunicorn along with Nginx. And be sure to modify settings.py for use in a production environment.

Download project and other dependencies:

	$ mkdir /www
	$ cd /www
	$ git clone https://github.com/danielstjules/labtracker.git
	$ virtualenv labtracker
	$ cd labtracker
	$ source bin/activate
	$ pip install django
	$ pip install xlwt

Setup MySQL DB:

	$ mysql -u user -p
	> CREATE DATABASE labdb;
	> CREATE USER 'db_user'@'localhost' IDENTIFIED BY 'password';
	> GRANT ALL PRIVILEGES ON labdb.* TO 'db_user'@'localhost';
	> exit

Modify website/settings.py, update DATABASES with your DB info:

	$ mv website/settings.example.py website/settings.py
	$ vi settings.py

Run syncdb and collectstatic:

	$ python manage.py syncdb
	$ python manage.py collectstatic

Run the server, and go to http://localhost to view it

	$ python manage.py runserver 0.0.0.0:8000

Importing items/equipment from a CSV:
-------------------------------------

Given existing data, one can import a csv to populate the MySQL db. As an example:

	$ mysql -u user -p --local-infile
	$ use labdb
	> load data local infile '/path/to/file.csv' into table labtracker_item fields terminated by ','
	enclosed by '"'
	lines terminated by '\n'
	(local_num,location,cfi,part_class,company,part_num,serial_num,asset_num,description,notes);

Generating Reports
------------------

![reports-screenshot](http://danielstjules.com/labtracker/reports.gif)

Labtracker requires [xlwt](https://pypi.python.org/pypi/xlwt) for generating Excel reports:

	$ pip install xlwt

Running Tests
-------------

Firstly, [django-dynamic-fixture](https://github.com/paulocheque/django-dynamic-fixture) is used to generate model instances for testing purposes. It can be installed by running:

	$ pip install django-dynamic-fixture

And [selenium](http://selenium-python.readthedocs.org/en/latest/) is used for functional tests. We use the FireFox WebDriver. Selenium can be installed using:

	$ pip install selenium

Then, to run the tests included in labtracker, simply navigate to the project folder and run:

	$ python manage.py test labtracker

Authors
-------

Application created by Daniel St. Jules, along with contributions from Vladimir Suse.

Licensing
---------

Licensed under the GPLv3. See LICENSE.txt for details.
