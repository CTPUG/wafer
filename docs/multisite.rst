.. _multisite:

==================
Multi-site support
==================

With multi-site support enabled, you can run multiple conferences from a single
Wafer instance.  Wafer multi-site support is based on the Django sites
framework and on the `django-multisite`_ module, but it's not enabled by
default.

.. _django-multisite: https://pypi.org/project/django-multisite/


Multi-site support is useful when you run recurring conferences organized by
the same group. There are a few advantages in doing so:

* attendees don't have to create new user accounts for every new conference.
* the server administration effort to run multiple events is almost the same as
  that for running a single one.


There are a few caveats, though:

* Running Django administrative will always act against the default site,
  unless you device some mechanism to avoid that. For example, setting the
  default site based on an environment variable.
* The default Django user permissions apply globally. Someone cannot be made a
  superuser on one conference without also being superuser in all others.

--------------------------
Enabling multisite support
--------------------------

To enable multi-site mode, there's two changes that you need to make to your
instance settings.

First, enable the multisite middleware::

    MIDDLEWARE = (
        # ....
       'multisite.middleware.DynamicSiteMiddleware',
        # ....
    )

Then define the default site by setting ``SITE_ID`` in one of the following
ways::

    # set default by ID
    from multisite import SiteID
    SITE_ID = SiteID(default=int(os.getenv("SITE_ID", "1")))

    # set default by domain name
    from multisite import SiteDomain
    SITE_ID = SiteDomain(default=of.getenv("SITE", "example.com"))

Notice that the above examples set the default site based on an environment
variable. This allows you to operate against specific sites when running Django
management commands, for example::

    $ SITE_ID=2 ./manage.py shell

    $ SITE=2020.myconference.com ./manage.py wafer_stats


There are several other settings that you may want to use. See
`django-multisite`_ for more datails.

--------------------
Managing conferences
--------------------

Managing multiple conferences in Wafer is the same as managing multiple sites
in other Django applications, with the exception that by using
`django-multisite`_ we can serve multiple conferences from the same application
instance.

To learn more, you can read the following documentation:

* `Django - The “sites” framework`_
* `django-multisite`_

.. _`Django - The “sites” framework`: https://docs.djangoproject.com/en/1.11/ref/contrib/sites/
