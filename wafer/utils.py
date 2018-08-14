import functools
import os
import unicodedata
from django.core.cache import caches
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.utils.decorators import method_decorator

from bakery.views import BuildableListView


def normalize_unicode(u):
    """Replace non-ASCII characters with closest ASCII equivalents
       where possible.
       """
    return unicodedata.normalize('NFKD', u).encode('ascii', 'ignore')


def order_results_by(*fields):
    """A decorator that applies an ordering to the QuerySet returned by a
       function.
       """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kw):
            result = f(*args, **kw)
            return result.order_by(*fields)
        return wrapper
    return decorator


def cache_result(cache_key, timeout):
    """A decorator for caching the result of a function."""
    def decorator(f):
        cache_name = settings.WAFER_CACHE

        @functools.wraps(f)
        def wrapper(*args, **kw):
            cache = caches[cache_name]
            result = cache.get(cache_key)
            if result is None:
                result = f(*args, **kw)
                cache.set(cache_key, result, timeout)
            return result

        def invalidate():
            cache = caches[cache_name]
            cache.delete(cache_key)

        wrapper.invalidate = invalidate
        return wrapper
    return decorator


class QueryTracker(object):
    """ Track queries to database. """

    def __enter__(self):
        from django.conf import settings
        from django.db import connection
        self._debug = settings.DEBUG
        settings.DEBUG = True
        del connection.queries[:]
        return self

    def __exit__(self, *args, **kw):
        from django.conf import settings
        settings.DEBUG = self._debug

    @property
    def queries(self):
        from django.db import connection
        return connection.queries[:]


class PaginatedBuildableListView(BuildableListView):
    """BuildableListView subclass that handles pagination"""

    build_prefix = '.'

    def build_queryset(self):
        """Override django-bakery's build logic to fake pagination."""
        paths = [(os.path.join(self.build_prefix, 'index.html'), {})]
        self.request = None
        queryset = self.get_queryset()
        paginator = self.get_paginator(queryset, self.get_paginate_by(queryset))
        for page in paginator.page_range:
            paths.append(
                (os.path.join(self.build_prefix, 'page',
                              '%d' % page, 'index.html'), {'page': page}))
        for build_path, kwargs in paths:
            self.request = self.create_request(build_path)
            # Add a user with no permissions
            self.request.user = AnonymousUser()
            # Fake context so views work as expected
            self.kwargs = kwargs
            self.prep_directory(build_path)
            target_path = os.path.join(settings.BUILD_DIR, build_path)
            self.build_file(target_path, self.get_content())
