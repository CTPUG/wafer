import os

from django.utils.translation import ugettext_lazy as _

# Django settings for wafer project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'wafer.db',
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Africa/Johannesburg'

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
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(project_root, 'bower_components'),
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

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'wafer.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wafer.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or
    # "C:/www/django/templates". Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'wafer.context_processors.site_info',
    'wafer.context_processors.menu_info',
    'wafer.context_processors.registration_settings',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django_medusa',
    'crispy_forms',
    'django_nose',
    'registration',
    'markitup',
    'wafer',
    'wafer.registration',
    'wafer.talks',
    'wafer.schedule',
    'wafer.users',
    'wafer.sponsors',
    'wafer.pages',
    'wafer.tickets',
)

# Only add south if we're on a version that doesn't support native migrations
# (native migrations were added in Django 1.7)
try:
    from django.db import migrations
    WAFER_NEEDS_SOUTH = False
except ImportError:
    INSTALLED_APPS += ('south', )
    WAFER_NEEDS_SOUTH = True


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
AUTH_PROFILE_MODULE = 'users.UserProfile'

AUTH_USER_MODEL = 'auth.User'

# Forms:
CRISPY_FAIL_SILENTLY = not DEBUG
CRISPY_TEMPLATE_PACK = 'bootstrap3'

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
)

# Log in with GitHub:
# AUTHENTICATION_BACKENDS = (
#     'django.contrib.auth.backends.ModelBackend',
#     'wafer.registration.backends.GitHubBackend',
# )
# WAFER_GITHUB_CLIENT_ID = 'register on github'
# WAFER_GITHUB_CLIENT_SECRET = 'to get these secrets'

# Set this to true to disable the login button on the navigation toolbar
WAFER_HIDE_LOGIN = False

# Talk submissions open
# Set this to False to disable talk submissions
WAFER_TALKS_OPEN = True

# Ticket registration with Quicket
# WAFER_TICKET_SECRET = "i'm a shared secret"

# django_medusa -- disk-based renderer
MEDUSA_RENDERER_CLASS = "wafer.management.static.WaferDiskStaticSiteRenderer"
MEDUSA_DEPLOY_DIR = os.path.join(project_root, 'static_mirror')
MARKITUP_FILTER = ('markdown.markdown', {'safe_mode': True})
