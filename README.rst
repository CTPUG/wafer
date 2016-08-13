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

Supported Django versions
=========================

Wafer supports Django 1.8 and Django 1.9.


Installation
============

1. ``pip install -r requirements.txt`` should install all the required
   python and django dependencies.

2. Wafer uses bower to manage javascript dependencies

   * Install bower in the static files base directory: ``npm install bower``

   * Grab the ``bower.json`` file to install the required javascript files
       ``./node_modules/bower/bin/bower install bower.json``

3. Install the wafer applications
   ``manage.py migrate``

4. If you don't have one yet, create a superuser with
   ``manage.py createsuperuser``.

5. Examine the ``settings.py`` file and create a
   ``localsettings.py`` file overriding the defaults
   as required.

   ``STATIC_FILES``, ``WAFER_MENUS``, ``MARKITUP_FILTER``,
   ``WAFER_TALKS_OPEN``, ``WAFER_REGISTRATION_OPEN`` and
   ``WAFER_PUBLIC_ATTENDEE_LIST`` will probably need to be
   overridden.

   If you add extensions to ``MARKITUP_FILTER``, be
   sure to install the appropriate python packages as well.

6. Log in and configure the Site:

   * The domain will be used as the base for e-mails sent during
     registration.

   * The name will be the conference's name.

7. Wafer uses the Django caching infrastructure in several places, so
   the cache table needs to be created using ``manage.py createcachetable``.

8. Create the default 'Page Editors' and 'Talk Mentors' groups using
   ``manage.py wafer_add_default_groups``.

9. Have a fun conference.

Installing Bootstrap
====================

The default templates and css files require jquery and bootstrap to work.

wafer provides a bower.json file to simplify the installation process. This
requires a working nodejs installation.

1. Install bower
   ``npm install bower``

2. Use bower to install appropriate versions of bootstrap and jquery
   ``$(npm bin)/bower install``

3. Move files to the correct location
   ``manage.py collectstatic``

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
