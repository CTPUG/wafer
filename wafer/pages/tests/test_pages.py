# Simple test of the edit logic around pages

from django.test import Client, TestCase, override_settings
from django.core.cache import caches

from wafer.pages.models import Page
from wafer.tests.utils import create_user


class PageEditTests(TestCase):

    def setUp(self):
        self.no_edit_user = create_user('no_edit')
        self.edit_user = create_user('can_edit', perms=('change_page',))

    def test_simple_page(self):
        # Test editing a page we create
        page = Page.objects.create(name="test edit page", slug="test_edit")
        page.save()
        c = Client()
        # Test without edit permission
        c.login(username=self.no_edit_user.username,
                password='no_edit_password')
        response = c.get('/test_edit/')
        templates = [x.name for x in response.templates]
        self.assertTrue('wafer.pages/page.html' in templates)
        response = c.get('/test_edit/', {'edit': ''})
        self.assertEqual(response.status_code, 403)
        c.logout()
        # Test with edit permission
        c.login(username=self.edit_user.username, password='can_edit_password')
        response = c.get('/test_edit/')
        templates = [x.name for x in response.templates]
        self.assertTrue('wafer.pages/page.html' in templates)
        response = c.get('/test_edit/', {'edit': ''})
        templates = [x.name for x in response.templates]
        self.assertTrue('wafer.pages/page_form.html' in templates)
        self.assertEqual(response.status_code, 200)

    def test_root_page(self):
        # Test editing /
        page = Page.objects.create(name="index", slug="index")
        page.save()
        c = Client()
        # Test without edit permission
        c.login(username=self.no_edit_user.username,
                password='no_edit_password')
        response = c.get('/index', follow=True)
        templates = [x.name for x in response.templates]
        self.assertTrue('wafer.pages/page.html' in templates)
        response = c.get('/index', {'edit': ''}, follow=True)
        templates = [x.name for x in response.templates]
        self.assertEqual(response.status_code, 403)
        c.logout()
        # Test with edit permission
        c.login(username=self.edit_user.username, password='can_edit_password')
        response = c.get('/index', follow=True)
        templates = [x.name for x in response.templates]
        self.assertTrue('wafer.pages/page.html' in templates)
        response = c.get('/index', {'edit': ''}, follow=True)
        templates = [x.name for x in response.templates]
        self.assertTrue('wafer.pages/page_form.html' in templates)
        self.assertEqual(response.status_code, 200)

    def test_cache_time(self):
        """Test the behaviour of cache_time"""
        uncached_page = Page.objects.create(name="not cached", slug="no_cache",
                                            content="*aa*")
        cached_page = Page.objects.create(name="Cached Page", slug="cached",
                                          content="*bb*",
                                          cache_time=100)
        # We use a memory cache here to actually check caching behaviour
        with override_settings(CACHES={"default": {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'},
                                       "wafer_cache": {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                                                       'LOCATION': 'test_cache'}}):
            cache = caches['wafer_cache']
            result = uncached_page.cached_render()
            self.assertEqual(result, uncached_page.content.rendered)
            self.assertEqual(cache.get(uncached_page._cache_key()), None)
            result = cached_page.cached_render()
            self.assertEqual(result, cached_page.content.rendered)
            self.assertEqual(cache.get(cached_page._cache_key()), result)
            # Check that updating the page content invalidates the cache
            cached_page.content = '*cc*'
            cached_page.save()
            self.assertEqual(cache.get(cached_page._cache_key()), None)
