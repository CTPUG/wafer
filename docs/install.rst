============
Installation
============

Supported versions
==================

wafer supports Django 1.7 and 1.8 and python 2.7, 3.4 and 3.5

Requirements
============

In addition to Django, wafer requires:

* django-crispy-forms
* django-registration-redux
* pyLibravatar
* django-medusa
* django-markitup

and their dependancies.

Basic instructions
==================


#. Install all the dependancies
   ``pip install -r requirements.txt``
 
   * If you are using Django 1.6, you will need to explicitly install
     south - ``pip install south``

#. Create the initial database schema
   ``manage.py migrate``

#. If you don't have one yet, create a superuser with
   ``manage.py createsuperuser``.

#. Log in and configure the Site:

   * The domain will be used as the base for emails sent during
     registration.

   * The name will be the conference's name.

   * By default, wafer assumes that the site will be accessible over ssl,
     so the registration emails will use an 'https' prefix. If this
     is not the case, override the wafer/registration/activation_email.txt
     template.

#. wafer uses the Django caching infrastructure in several places, so
   the cache table needs to be created using ``manage.py createcachetable``.

#. Create the default 'Page Editors' and 'Talk Mentors' groups using
   ``manage.py wafer_add_default_groups``.

#. Ensure the permissions on the MEDIA_ROOT directory are correctly set so the
   webserver can create new files there. This location is used for files uploaded
   for pages and sponsor information.

#. Have a fun conference.

Using Django 1.6 and Python 3
-----------------------------

South 1.0 fails with python 3, described `in this issue`_. To properly support
python 3 and Django 1.6, you need to install a patched version. The following
command should work::

    pip install 'https://bitbucket.org/andrewgodwin/south/get/e2c9102ee033.zip#egg=South

.. _in this issue: https://bitbucket.org/andrewgodwin/south/pull-request/162/fixed-a-python-3-incompatibility-by


Important settings
==================

``TALKS_OPEN`` controls whether talk submissions are accepted. Set to False to close talk submissions.

``WAFER_MENUS`` adds the top level menu items for the site. 



