import functools
import unicodedata
from django.core.cache import caches
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


def normalize_unicode(u):
    """Replace non-ASCII characters with closest ASCII equivalents
       where possible.
       """
    return unicodedata.normalize('NFKD', u).encode('ascii', 'ignore')


def cache_result(cache_key, timeout):
    """A decorator for caching the result of a function."""
    def decorator(f):
        cache_name = settings.WAFER_CACHE

        @functools.wraps(f)
        def wrapper(*args, **kw):
            # replace this with cache.caches when we drop Django 1.6
            # compatibility
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


# XXX: Should we use Django's version for Django >= 1.9 ?
# This should certainly go away when we drop support for
# Django 1.8
class LoginRequiredMixin(object):
    '''Must be logged in'''
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)
