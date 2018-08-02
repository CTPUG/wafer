========
Sponsors
========

Packages
========

Sponsor packages describe the details of the various sponsor packages
available.

The ``order`` field controls the order in which packages are listed on the
sponsor packages page.


Sponsors
========

This is used to add details of the sponsors.

The description can be formatted using markdown syntax.

Images can be uploaded and used in the description using the files field.

Files
=====

Additional files, such as images, can be uploaded so they can be referenced.
These files are placed in ``MEDIA_ROOT/sponsors_files`` by default. This
location needs to be writeable by the webserver for uploads to work.

Using files in templates
------------------------

Uploaded files can be associated with a sponsor and a name in the admin
interface which can be used with the ``sponsor_tagged_image`` templatetag
in the templates.

The default wafer sponsor templates expect each sponsor to have an image
labelled ``main_logo`` for use in the sponsor list.

Wafer also provides an example template block for adding sponsors as a
footer to pages called ``sponsors_footer``. This expects images
labelled ``footer_logo``.
