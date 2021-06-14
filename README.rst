wafer
=====

|wafer-ci-badge| |wafer-docs-badge| |wafer-weblate-badge|

.. |wafer-ci-badge| image:: https://travis-ci.org/CTPUG/wafer.png?branch=master
    :alt: Travis CI build status
    :scale: 100%
    :target: https://travis-ci.org/CTPUG/wafer

.. |wafer-docs-badge| image:: https://readthedocs.org/projects/wafer/badge/?version=latest
    :alt: Wafer documentation
    :scale: 100%
    :target: https://wafer.readthedocs.org/

.. |wafer-weblate-badge| image:: https://hosted.weblate.org/widgets/wafer/-/svg-badge.png
    :alt: Translation status
    :scale: 100%
    :target: https://hosted.weblate.org/engage/wafer/

A wafer-thin web application for running small conferences. Built using Django.

Licensed under the `ISC License`_.

.. _ISC License: https://github.com/CTPUG/wafer/blob/master/LICENSE


Documentation
=============

Available on `readthedocs.org`_.

.. _readthedocs.org: https://wafer.readthedocs.org/

Supported Django versions
=========================

Wafer supports Django 2+ and Django 3.0.

Installation
============

1. wafer can be installed either from pypi (``pip install wafer``)
   or from the github repository.

2. If installing from github, ``pip install -r requirements.txt``
   should install all the required python and django dependencies.

3. Wafer uses npm to manage front-end dependencies

   * Make sure you have a recent version of Node.js installed that
     includes ``npm``.

   * Run ``npm install`` to install all dependencies, which also copies
     them to ``wafer/static/vendor``.

4. Install the wafer applications
   ``manage.py migrate``

5. If you don't have one yet, create a superuser with
   ``manage.py createsuperuser``.

6. Examine the ``settings.py`` file and create a
   ``localsettings.py`` file overriding the defaults
   as required.

   ``STATIC_FILES``, ``WAFER_MENUS``, ``MARKITUP_FILTER``,
   ``WAFER_PAGE_MARKITUP_FILTER``, ``WAFER_TALKS_OPEN``,
   ``WAFER_REGISTRATION_OPEN`` and ``WAFER_PUBLIC_ATTENDEE_LIST`` will
   probably need to be overridden.

   If you add extensions to ``MARKITUP_FILTER`` or
   ``WAFER_PAGE_MARKITUP_FILTER``, be sure to install the appropriate
   python packages as well.

7. Wafer uses the Django caching infrastructure in several places, so
   the cache table needs to be created using ``manage.py createcachetable``.

8. Create the default 'Page Editors' and 'Talk Mentors' groups using
   ``manage.py wafer_add_default_groups``.

9. Log in and configure the Site:

   * The domain will be used as the base for e-mails sent during
     registration.

   * The name will be the conference's name.

10. Have a fun conference.

Running wafer
=============

To run a local server for development and testing, use the standard Django
``manage.py runserver``, after doing the installation.

For running the server in production, please see the `Django documentation`_
on the various possible approaches.

.. _Django documentation: https://docs.djangoproject.com/en/3.0/howto/deployment/

Features
========

* Support for adding and editing sponsors via Django admin.
* Schedule can be created and updated via Django admin.
* Pages for static content, news and so forth can be handled via Django admin.

  * Can be delegated to the 'Page Editors' group.
  * Pages can be updated via the web interface.

* Talk submissions, review and acceptance.
* Generate a static version of the site for archival.

Translation
===========

Translations for wafer are managed at `weblate.org`_

.. _weblate.org: https://hosted.weblate.org/projects/wafer/
