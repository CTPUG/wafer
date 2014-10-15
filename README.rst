wafer
=====

|wafer-ci-badge| |wafer-docs-badge|

.. |wafer-ci-badge| image:: https://travis-ci.org/CTPUG/wafer.png?branch=master
    :alt: Travis CI build status
    :scale: 100%
    :target: https://travis-ci.org/CTPUG/wafer

.. |wafer-docs-badge| image:: https://readthedocs.org/projects/wafer/badge/?version=latest
    :alt:  Wafer documentation
    :scale: 100%
    :target: http://wafer.readthedocs.org/

A wafer-thin web application for running small conferences. Built using Django.

Licensed under the `ISC License`_.

.. _ISC License: https://github.com/CTPUG/wafer/blob/master/LICENSE


Documentation
=============

Available on `readthedocs.org`_.

.. _readthedocs.org: http://wafer.readthedocs.org/


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

Running with Django 1.6
-----------------------

If you are running Django 1.6, please also install south for migrations::

    pip install south

South 1.0 fails with python 3, described `in this issue`_. To properly support
python 3 and Django 1.6, you need to install a patched version. The following
command should work::

    pip install 'https://bitbucket.org/andrewgodwin/south/get/e2c9102ee033.zip#egg=South

.. _in this issue: https://bitbucket.org/andrewgodwin/south/pull-request/162/fixed-a-python-3-incompatibility-by


Features
========

* Support for adding and editing sponsors via Django admin.
* Schedule can be created and updated via Django admin.
* Pages for static content, news and so forthe can be handled via Django admin.

  * Can be delegated to the 'Page Editors' group.
  * Pages can be updated via the web interface.

* Talk submissions and acceptance.
* Generate a static version of the site for archival.


TODO
====

* Make the code easier to use for other conferences (split out theming, etc).
* Improve the talk submission management module:

  * Better display of accepted talks.

* Make various messages easier to customise.
* Improve admin support for the schedule:

  * Show table of slots in admin interface.
  * Improve handling of moving talks around.

* Support for adding news (and other templated pages) via Django admin.
* Maybe add some cool visualizations with d3:

  * Number of people signed up in various categories.
  * Places remaining.
  * Sponsorship slots remaining.
  * Days until various deadlines.

* Other improvements
* Add many tests
