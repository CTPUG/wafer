import os

from django.utils.translation import ugettext_lazy as _

try:
    from localsettings import *
except ImportError:
    pass

# Django settings for wafer project.

ADMINS = (
    # The logging config below mails admins
    # ('Your Name', 'your_email@example.com'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'wafer.db',
    }
}

if os.environ.get('TESTDB', None) == 'postgres':
    DATABASES['default'].update({
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'postgres',
        'NAME': 'wafer',
        })

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MEDIA_ROOT = os.path.join(project_root, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(project_root, 'static')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '8iysa30^no&oi5kv$k1w)#gsxzrylr-h6%)loz71expnbf7z%)'

TEMPLATES = [
    {
        'APP_DIRS': True,
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (
            # Put strings here, like "/home/html/django_templates" or
            # "C:/www/django/templates". Always use forward slashes, even on Windows.
            # Don't forget to use absolute paths, not relative paths.
        ),
        'OPTIONS': {
            'context_processors': (
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'wafer.context_processors.site_info',
                'wafer.context_processors.navigation_info',
                'wafer.context_processors.menu_info',
                'wafer.context_processors.registration_settings'
            )
        }
    },
]


MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'wafer.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wafer.wsgi.application'


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.redirects',
    'reversion',
    'bakery',
    'crispy_forms',
    'django_nose',
    'rest_framework',
    'easy_select2',
    'wafer',
    'wafer.kv',
    'wafer.registration',
    'wafer.talks',
    'wafer.schedule',
    'wafer.users',
    'wafer.sponsors',
    'wafer.pages',
    'wafer.tickets',
    'wafer.compare',
    # Django isn't finding the overridden templates
    'markitup',
    'registration',
    'django.contrib.admin',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Django registration:
ACCOUNT_ACTIVATION_DAYS = 7

AUTH_USER_MODEL = 'auth.User'

# Forms:
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Wafer cache settings
# We assume that the WAFER_CACHE is cross-process
WAFER_CACHE = 'wafer_cache'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    WAFER_CACHE: {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'wafer_cache_table',
    },
}


# Wafer menu settings

WAFER_MENUS = ()
# Example menus entries:
#
#    {"label": _("Home"),
#     "url": '/'},
#    {"menu": "sponsors",
#     "label": _("Sponsors"),
#     "items": [
#         {"name": "sponsors", "label": _("Our sponsors"),
#          "url": reverse_lazy("wafer_sponsors")},
#         {"name": "packages", "label": _("Sponsorship packages"),
#          "url": reverse_lazy("wafer_sponsorship_packages")},
#     ]},
#    {"label": _("Talks"),
#     "url": reverse_lazy("wafer_users_talks")},

WAFER_DYNAMIC_MENUS = (
    'wafer.pages.models.page_menus',
    'wafer.sponsors.models.sponsor_menu',
)

# Enabled SSO mechanims:
WAFER_SSO = (
    # 'github',
    # 'debian',
)

# Log in with GitHub:
# WAFER_GITHUB_CLIENT_ID = 'register on github'
# WAFER_GITHUB_CLIENT_SECRET = 'to get these secrets'

# Log in with Debian SSO:
# Requires some Apache config:
# SSLCACertificateFile /srv/sso.debian.org/etc/debsso.crt
# SSLCARevocationCheck chain
# SSLCARevocationFile /srv/sso.debian.org/etc/debsso.crl
# <Location /accounts/debian-login/>
#     SSLOptions +StdEnvVars
#     SSLVerifyClient optional
# </Location>
# WAFER_DEBIAN_NM_API_KEY = 'obtain one from https://nm.debian.org/apikeys/'

# Set this to true to disable the login button on the navigation toolbar
WAFER_HIDE_LOGIN = False

# Talk submissions open
# Set this to False to disable talk submissions
WAFER_TALKS_OPEN = True

# The form used for talk submission
WAFER_TALK_FORM = 'wafer.talks.forms.TalkForm'

# Ask speakers for video release, and an email address of a reviewer
WAFER_VIDEO = True
WAFER_VIDEO_REVIEWER = True
WAFER_VIDEO_LICENSE = 'CC BY-SA 4.0'
WAFER_VIDEO_LICENSE_URL = 'https://creativecommons.org/licenses/by-sa/4.0/'

# Range of scores for talk reviews (inclusive)
WAFER_TALK_REVIEW_SCORES = (-2, 2)

# Set this to False to disable registration
WAFER_REGISTRATION_OPEN = True

# WAFER_REGISTRATION_MODE can be 'ticket' for Quicket tickets, or 'custom' if
# you implement your own registration system. If 'custom', then you *must*
# define a URL named 'register' in your application so we can link to it.
WAFER_REGISTRATION_MODE = 'ticket'
# WAFER_USER_IS_REGISTERED should return a boolean, when passed a Django user.
WAFER_USER_IS_REGISTERED = 'wafer.tickets.models.user_is_registered'

# Allow registered and anonymous users to see registered users
WAFER_PUBLIC_ATTENDEE_LIST = True

# Ticket registration with Quicket
# WAFER_TICKET_SECRET = "i'm a shared secret"

# django-bakery -- disk-based renderer
BUILD_DIR = os.path.join(project_root, 'static_mirror')

MARKITUP_FILTER = ('markdown.markdown', {'safe_mode': True})
JQUERY_URL = 'vendor/jquery/dist/jquery.min.js'
SELECT2_USE_BUNDLED_JQUERY = False

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 50
}

BAKERY_VIEWS = (
    'wafer.pages.views.ShowPage',
    'wafer.schedule.views.VenueView',
    'wafer.schedule.views.ScheduleView',
    'wafer.schedule.views.ScheduleXmlView',
    'wafer.sponsors.views.ShowSponsors',
    'wafer.sponsors.views.ShowPackages',
    'wafer.sponsors.views.SponsorView',
    'wafer.talks.views.TalkView',
    'wafer.talks.views.Speakers',
    'wafer.talks.views.TracksView',
    'wafer.talks.views.TalkTypesView',
    'wafer.talks.views.UsersTalks',
    'wafer.users.views.UsersView',
    'wafer.users.views.ProfileView',
)
