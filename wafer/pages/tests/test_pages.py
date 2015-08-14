# Simple test of the edit logic around pages

from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from wafer.pages.models import Page


class PageEditTests(TestCase):

    def _make_users(self):
        # utiltiy function for tests
        UserModel = get_user_model()

        # Make user without edit permissions
        try:
            no_edit_user = UserModel.objects.filter(username='no_edit').get()
        except UserModel.DoesNotExist:
            no_edit_user = UserModel.objects.create_user('no_edit',
                                                         'test@test',
                                                         'aaaa')
            no_edit_user.save()

        # Make user with edit permissions
        try:
            edit_user = UserModel.objects.filter(username='can_edit').get()
        except UserModel.DoesNotExist:
            edit_user = UserModel.objects.create_user('can_edit',
                                                      'test@test',
                                                      'aaaa')
            # Is there a better way to do this?
            page_content_type = ContentType.objects.get_for_model(Page)
            change_page = Permission.objects.get(
                content_type=page_content_type, codename='change_page')

            edit_user.user_permissions.add(change_page)
            edit_user.save()

        return no_edit_user, edit_user

    def test_simple_page(self):
        # Test editing a page we create
        no_edit_user, edit_user = self._make_users()
        page = Page.objects.create(name="test edit page", slug="test_edit")
        page.save()
        c = Client()
        # Test without edit permission
        c.login(username=no_edit_user.username, password='aaaa')
        response = c.get('/test_edit')
        templates = [x.name for x in response.templates]
        self.assertTrue('wafer.pages/page.html' in templates)
        response = c.get('/test_edit', {'edit': ''})
        self.assertEqual(response.status_code, 403)
        c.logout()
        # Test with edit permission
        c.login(username=edit_user.username, password='aaaa')
        response = c.get('/test_edit')
        templates = [x.name for x in response.templates]
        self.assertTrue('wafer.pages/page.html' in templates)
        response = c.get('/test_edit', {'edit': ''})
        templates = [x.name for x in response.templates]
        self.assertTrue('wafer.pages/page_form.html' in templates)
        self.assertEqual(response.status_code, 200)

    def test_root_page(self):
        # Test editing /
        no_edit_user, edit_user = self._make_users()
        page = Page.objects.create(name="index", slug="index")
        page.save()
        c = Client()
        # Test without edit permission
        c.login(username=no_edit_user.username, password='aaaa')
        response = c.get('/index', follow=True)
        templates = [x.name for x in response.templates]
        self.assertTrue('wafer.pages/page.html' in templates)
        response = c.get('/index', {'edit': ''}, follow=True)
        templates = [x.name for x in response.templates]
        self.assertEqual(response.status_code, 403)
        c.logout()
        # Test with edit permission
        c.login(username=edit_user.username, password='aaaa')
        response = c.get('/index', follow=True)
        templates = [x.name for x in response.templates]
        self.assertTrue('wafer.pages/page.html' in templates)
        response = c.get('/index', {'edit': ''}, follow=True)
        templates = [x.name for x in response.templates]
        self.assertTrue('wafer.pages/page_form.html' in templates)
        self.assertEqual(response.status_code, 200)
