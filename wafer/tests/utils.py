"""Utilities for testing wafer."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import tag
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

try:
    # Guard for running this without selenium installed
    from selenium import webdriver
except ImportError:
    selenium = None


def get_group(group):
    return Group.objects.get(name=group)


def create_group(group):
    return Group.objects.create(name=group)


def create_user(username, email=None, superuser=False, perms=(), groups=()):
    if superuser:
        create = get_user_model().objects.create_superuser
    else:
        create = get_user_model().objects.create_user
    if email is None:
        email = "%s@example.com" % username
    user = create(username, email, "%s_password" % username)
    for codename in perms:
        perm = Permission.objects.get(codename=codename)
        user.user_permissions.add(perm)
    for group_name in groups:
        group = Group.objects.get(name=group_name)
        user.groups.add(group)
    if perms or groups:
        user = get_user_model().objects.get(pk=user.pk)
    return user


def mock_avatar_url(self):
    """Avoid libravatar DNS lookups during tests"""
    if self.user.email is None:
        return None
    return "avatar-%s" % self.user.email

@tag('selenium')
class BaseWebdriverRunner(StaticLiveServerTestCase):

    def setUp(self):
        """Create an ordinary user and an admin user for testing"""
        if not selenium:
            raise RuntimeError("Test requires selenium installed")
        super().setUp()
        self.admin_user = create_user('admin', email='admin@localhost', superuser=True)
        self.admin_password = 'admin_password'
        self.normal_user = create_user('normal', email='normal@localhost', superuser=False)
        self.normal_password = 'normal_password'

    def normal_login(self):
        """Login as an ordinary user"""

    def admin_login(self):
        """Login as the admin user"""


@tag('chrome')
class ChromeTestRunner(BaseWebdriverRunner):

    def setUp(self):
        super().setUp()
        # Load the chrome webdriver


@tag('firefox')
class FirefoxTestRunner(BaseWebdriverRunner):

    def setUp(self):
        super().setUp()
        # Load the firefox webdriver
