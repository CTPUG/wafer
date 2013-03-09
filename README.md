wafer
=====

[![Build Status](https://travis-ci.org/CTPUG/wafer.png?branch=master)](https://travis-ci.org/CTPUG/wafer)

A wafer-thin web application for running small conferences. Built using Django.

Licensed under the [ISC License](LICENSE).


TODO
====

* Make the code easier to use for other conferences (split out theming, etc)
* Add support for editing talk submissions.
* Add support for editing and arranging the schedule via Django admin.
* Better invoice management
  * Invoices should be a separate table.
  * Invoices should be creatable in Django admin.
  * Allow multiple invoices per person.
  * Allow multiple people per invoice.
  * Allow cancelling (but not deletion) of invoices.
* Support for adding news (and other templated pages) via Django admin.
* Support for adding and editing sponsors via Django admin.
* Maybe add some cool visualizations with  d3:
  * Number of people signed up in various categories.
  * Places remaining.
  * Sponsorship slots remaining.
  * Days until various deadlines.
* Other improvements

