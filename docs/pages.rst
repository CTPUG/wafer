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
A page with the slug ``announcements`` and the parent ``news`` will have a URL
of ``/news/announcements``

Container pages
===============

Container pages are created to act as parents for other pages. These should
have minimal content, as they will typically not be displayed on the site,
and should be excluded from the static site generation.

Files
=====

Additional files, such as images, can be uploaded so they can be
referenced in page.  These files are placed in
``MEDIA_ROOT/pages_files`` by default. This location needs to be
writeable by the webserver for uploads to work.

Maintaining pages in files
==========================

Pages live in the database, and can be edited through the web UI.
However, it can be useful to store them in files (e.g. in a git repo,
with the site source code).

There is a management command (``load_pages``) that will read pages from
files into the database.
It requires ``PyYAML`` to be installed.

Pages must be stored as markdown in a directory, in the same hierarchy
as the desired URL structure.
The ``PAGE_DIR`` Django setting should be an absolute path to root
directory of this hierarchy, beginning and ending with ``/``.
e.g.::

    /app/pages/                         ← PAGE_DIR
    /app/pages/index.md                 ← Home Page: /
    /app/pages/about.md                 ← Container Page: /about/
    /app/pages/about
    /app/pages/about/the-conference.md  ← /about/the-conference/

Each page starts with a YAML front-matter (similar to Jekyll), and is
then followed by the Markdown page body.
e.g. ``pages/index.md``::

    ---
    name: Index
    ---
    Welcome to Foo Conf (not Foo Conf, that's another thing entirely)!

    We invite you to [join us](/attend/) at [our venue](/venue/)
    on the 31st of December for a day of fun conferencing.

The front matter can contain a couple of flags:

``published``
    If set to ``false``, the page will not be loaded by the
    ``load_pages`` command.
``include_in_menu``
    If set to ``true``, the page will be added to the menu structure.
``exclude_from_static``
    If set to ``true``, the page will not be archived to static HTML by
    :ref:`staticsitegen <staticsitegen>`.
