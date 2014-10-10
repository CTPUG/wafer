============
Installation
============

Supported versions
==================

wafer supports Django 1.6 and 1.7 and python 2.6 and 2.7.
Note that Django 1.7 only supports python 2.7.

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

#. Create the intial database schema
   ``manage.py migrate``

#. If you don't have one yet, create a superuser with
   ``manage.py createsuperuser``.

#. Log in and configure the Site:

   * The domain will be used as the base for e-mails sent during
     registration.

   * The name will be the conference's name.

#. Create the default 'Page Editors' and 'Talk Mentors' groups using
   ``manage.py wafer_add_default_groups``.

#. Have a fun conference.


Important settings
==================

``TALKS_OPEN`` controls wether talk submissions are accepted. Set to False to close talk submissions.

``WAFER_MENUS`` adds the top level menu items for the site. 



