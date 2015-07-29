=====
Pages
=====

Basic pages
===========

Pages are used to describe static information for the conference.

The contents can be formatted using markdown syntax and images can be
uploaded using the ``files`` field.

The ``slug`` defines the last part of the path.

The parent field is used to group the page under specific parts of the namespace.
A page with the slug ``announcements`` and the parent ``news`` will have a url
of ``/news/announcements``

Container pages
===============

Container pages are created to act as parents for other pages. These should
have minimal content, as they will typically not be displayed on the site,
and should be excluded from the static site generation.

Files
=====

Additional files, such as images, can be uploaded so they can be referenced in page.
These files are placed in MEDIA_ROOT/pages_files by default. This location needs to
be writable by the webserver for uploads to work.
