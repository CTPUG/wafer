============
Installation
============

Basic instructions
==================

1. Create the intial database schema
   ``manage.py migrate``

2. If you don't have one yet, create a superuser with
   ``manage.py createsuperuser``.

3. Log in and configure the Site:

   * The domain will be used as the base for e-mails sent during
     registration.

   * The name will be the conference's name.

4. Create the default 'Page Editors' and 'Talk Mentors' groups using
   ``manage.py wafer_add_default_groups``.

5. Have a fun conference.


Important settings
==================

``TALKS_OPEN`` controls wether talk submissions are accepted. Set to False to close talk submissions.

``WAFER_MENUS`` adds the top level menu items for the site. 



