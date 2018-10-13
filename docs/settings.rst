.. _settings:

--------
Settings
--------

Wafer has several Django settings that control its behaviour.
It attempts to provide reasonable defaults for these, (and Django in general),
in the ``wafer.settings`` module, so you can import this in your app's
``settings.py``, and then override things you want to change.


Wafer's settings
================

``PAGE_DIR``
    The directory that the ``load_pages`` management command will load
    pages from.
    Should be an absolute path with a trailing ``/``.

``TALKS_OPEN``
    Controls whether talk submissions are accepted.
    Set to ``False`` to close talk submissions.

``WAFER_CACHE``
    The name of the Django cache backend that wafer can use.
    Defaults to ``'wafer_cache'``.

``WAFER_DEBIAN_NM_API_KEY``
    The API Key for ``nm.debian.org``'s API, used by Debian SSO.
    Used when ``WAFER_SSO`` contains ``'debian'``.

``WAFER_DYNAMIC_MENUS``
    A list of functions to call to generate additional menus.

``WAFER_GITHUB_CLIENT_ID``
    The client ID for GitHub SSO.
    Used when ``WAFER_SSO`` contains ``'github'``.
    If you set this up, they'll provide you with one.

``WAFER_GITHUB_CLIENT_SECRET``
    The secret for GitHub SSO.
    Used when ``WAFER_SSO`` contains ``'github'``.
    If you set this up, they'll provide you with one.

``WAFER_HIDE_LOGIN``
    A boolean flag.
    When ``True``, the login link in the menu is hidden.
    This is useful to set, before making a site static.

``WAFER_SSO``
    A list of SSO mechanisms in use.
    Possible options are: ``'debian'``, ``'github'``.

``WAFER_TALK_FORM``
    The form used for talk/event submission.
    There is a reasonable default form, but this can be changed to
    customise the submission process.

``WAFER_MENUS``
    Static menu structure for the site.
    This is a list of dicts, with the keys:

    ``label``
        The text in the menu.

    ``url``
        The URL to link to.

    ``items``
        An optional list of similar dicts, making up a submenu.

``WAFER_PUBLIC_ATTENDEE_LIST``
    A boolean flag.
    When ``True``, all registered users' profiles are publicly visible.
    Otherwise, only users with associated public talks have public
    profiles.

``WAFER_REGISTRATION_MODE``
    The mechanisms users will register for the conference, with.
    Possible options are:

    ``'ticket'``
        For Quicket integration. The default.

    ``'custom'``
        For your own implementation. See ``WAFER_USER_IS_REGISTERED``.

``WAFER_REGISTRATION_OPEN``
    A boolean flag.
    When ``True``, users can register for the conference.
    (Note, this is not the same as signing up for an account on the website.)

``WAFER_TALK_REVIEW_SCORES``
    A tuple of 2 integers.
    The range of values for talk reviews. Inclusive.

``WAFER_TALKS_OPEN``
    A boolean flag.
    When ``True``, users can submit talks.

``WAFER_TICKETS_SECRET``
    The secret for the Quicket API.
    Used when ``WAFER_REGISTRATION_MODE`` is ``'ticket'``.

``WAFER_USER_IS_REGISTERED``
    A function, which takes a user, and determines if they have
    registered for attendance at the conference.
    It should return a boolean result.
    The default function checks for a Quicket ticket.

``WAFER_VIDEO``
    A boolean flag.
    When ``True``, the default talk submission form will ask for a video
    release from the submitter.

``WAFER_VIDEO_REVIEWER``
    A boolean flag.
    When ``True``, the default talk submission form will ask for the
    email address of someone who will review the talk's video, once it
    is ready to publish.

``WAFER_VIDEO_LICENSE``
    The name of the license that the conference's videos will be
    released under. Talk submitters will be asked to release their video
    under this license.

``WAFER_VIDEO_LICENSE_URL``
    Link to the full text of ``WAFER_VIDEO_LICENSE``.

Third party settings
====================

Some libraries that wafer uses have settings that you may want to
configure.
This is a non-complete list of them, see the individual project's
documentation for more details.

``ACCOUNT_ACTIVATION_DAYS``
    Used by `django-registration-redux`_.
    Number of days that users have to click the account activation link
    that was emailed to them.

``MARKITUP_FILTER``
    Configuration for `django-markitup`_.
    The type of markup used for pages, talk abstracts, user profiles,
    and other things.
    Also, configuration for the conversion, such as allowing arbitrary
    HTML embedding.

``BUILD_DIR``
    Used by `django-bakery`_.
    The directory that static versions of the sites are rendered to.

``REGISTRATION_OPEN``
    Boolean flag.
    Used by `django-registration-redux`_.
    When ``True``, user sign-up is permitted.

.. _django-markitup: https://github.com/zsiciarz/django-markitup
.. _django-bakery: https://github.com/datadesk/django-bakery
.. _django-registration-redux: https://django-registration-redux.readthedocs.io/
