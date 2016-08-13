============
Installation
============

Supported versions
==================

Wafer supports Django 1.8 and 1.9 and python 2.7, 3.4 and 3.5.

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

#. Wafer uses the Django caching infrastructure in several places, so
   the cache table needs to be created using ``manage.py createcachetable``.

#. Create the default 'Page Editors' and 'Talk Mentors' groups using
   ``manage.py wafer_add_default_groups``.

#. Ensure the permissions on the MEDIA_ROOT directory are correctly set so the
   webserver can create new files there. This location is used for files uploaded
   for pages and sponsor information.

#. Have a fun conference.

Important settings
==================

``TALKS_OPEN`` controls whether talk submissions are accepted. Set to False to close talk submissions.

``WAFER_MENUS`` adds the top level menu items for the site. 



