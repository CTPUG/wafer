wafer
=====

[![Build Status](https://travis-ci.org/CTPUG/wafer.png?branch=master)](https://travis-ci.org/CTPUG/wafer)

A wafer-thin web application for running small conferences. Built using Django.

Licensed under the [ISC License](LICENSE).

Installation
============

1. TODO: Explain it all

2. If you don't have one yet, create a superuser with
   ``manage.py createsuperuser``.

3. Log in and configure the Site:

   * The domain will be used as the base for e-mails sent during
     registration.

   * The name will be the conference's name.

4. Create the default 'Page Editors' and 'Talk Mentors' groups using
   ``manage.py wafer_add_default_groups``.

5. Have a fun conference.

Features
========

* Support for adding and editing sponsors via Django admin.


TODO
====

* Improve the dashboard for logged in users showing them:
  * A list of their invoices (and whether they're finalized / paid).
* Make the code easier to use for other conferences (split out theming, etc)
* Improve the talk submission management module
  * Use markdown to allow better formatting of talk abstracts
  * Better display of accepted talks
* Finish the conference registration module
  * Make various messages easier to customise
* Add support for editing and arranging the schedule via Django admin.
* Better invoice management
  * Invoices should be a separate table.
  * Invoices should be creatable in Django admin.
  * Allow multiple invoices per person.
  * Allow multiple people per invoice.
  * Allow cancelling (but not deletion) of invoices.
* Support for adding news (and other templated pages) via Django admin.
* Maybe add some cool visualizations with  d3:
  * Number of people signed up in various categories.
  * Places remaining.
  * Sponsorship slots remaining.
  * Days until various deadlines.
* Other improvements
* Add tests

