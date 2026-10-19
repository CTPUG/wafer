"""Tests for logging out from the menu"""

from django.test import Client, TestCase
from django.urls import reverse

from wafer.tests.utils import create_user


class LogoutTests(TestCase):

    def setUp(self):
        create_user('test1')
        self.client = Client()
        self.client.login(username='test1', password='test1_password')

    def test_menu_logs_out_with_post(self):
        """Django 5 only allows logging out with POST, so the menu needs a
           form, not a link."""
        response = self.client.get(reverse('wafer_users_talks'))
        logout_url = reverse('auth_logout')
        self.assertContains(response, 'action="%s"' % logout_url)
        self.assertNotContains(response, 'href="%s"' % logout_url)

    def test_logout_with_post(self):
        self.assertIn('_auth_user_id', self.client.session)
        self.client.post(reverse('auth_logout'))
        self.assertNotIn('_auth_user_id', self.client.session)
