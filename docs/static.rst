.. _staticsitegen:

======================
Static Site Generation
======================

Usage
=====

The ``manage.py build`` command will generate a static version
of the site using django-bakery.

The static site will include pages, talks, sponsors and user details.

You need to exclude container pages used for the menus from the static
site using the "exclude from static" option in the admin interface,
otherwise it will attempt to create files with the same name as the
containing directories and the export will fail. If this happens, simply
correct the problematic pages and rerun the command.

We suggest setting ``WAFER_HIDE_LOGIN`` to ``True`` when generating the
static site so there is no login button on the static site.
