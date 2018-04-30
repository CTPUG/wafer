============
Installation
============

Supported versions
==================

Wafer supports Django 1.11-2.0 and Python 2.7, 3.4-3.6.

Requirements
============

In addition to Django, wafer has some requirements on external
libraries. They're listed in ``setup.py``.

Basic Dev install
=================

#. Install all the dependencies
   ``pip install -r requirements.txt``
 
#. Create the initial database schema
   ``manage.py migrate``

#. If you don't have one yet, create a superuser with
   ``manage.py createsuperuser``.

#. Log in and configure the Site:

   * The domain will be used as the base for emails sent during
     registration.

   * The name will be the conference's name.

   * By default, wafer assumes that the site will be accessible over SSL,
     so the registration emails will use an 'https' prefix. If this
     is not the case, override the ``wafer/registration/activation_email.txt``
     template.

#. Wafer uses the Django caching infrastructure in several places, so
   the cache table needs to be created using ``manage.py createcachetable``.

#. Create the default 'Page Editors', 'Talk Mentors', and 'Talk
   Reviewers' groups using ``manage.py wafer_add_default_groups``.

#. Ensure the permissions on the ``MEDIA_ROOT`` directory are correctly
   set so the webserver can create new files there. This location is
   used for files uploaded for pages and sponsor information.

#. Have a fun conference.

Recommended production setup
============================

#. Create a new Django app, in your own VCS repository. Add wafer
   (probably pinned) as a requirement.

#. Include wafer's ``wafer.settings`` in your ``settings.py``::

       from wafer.settings import *

       TIME_ZONE = 'Africa/Johannesburg'
       ...

#. You'll want to include wafer's default values for some settings, e.g.
   ``INSTALLED_APPS``, rather than completely overriding them.
   See :ref:`settings` for the wafer-specific settings.

#. Override templates as necessary, by putting your own templates
   directory early in ``TEMPLATES``.

#. And then continue with the basic instructions above.


Example setup
=============

For an example of a conference using wafer, see the 2017 PyCon ZA
conference repository, available from `github`_


.. _github: https://github.com/CTPUG/pyconza2017
