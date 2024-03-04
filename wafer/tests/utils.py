"""Utilities for testing wafer."""

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import tag
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from wafer.users.models import PROFILE_GROUP

try:
    # Guard for running this without selenium installed
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions
except ImportError:
    webdriver = None


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


# Time to wait for elements to appear - single constant so we can easily tune it if needed
WAIT_TIME = 20


@tag('selenium')
class BaseWebdriverRunner(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        """Create the driver instance"""
        if not webdriver:
            raise RuntimeError("Test requires selenium installed")
        super().setUpClass()

    def setUp(self):
        """Create an ordinary user and an admin user for testing"""
        super().setUp()
        self.admin_user = create_user('admin', email='admin@localhost', superuser=True)
        self.admin_password = 'admin_password'
        self.normal_user = create_user('normal', email='normal@localhost', superuser=False)
        self.normal_password = 'normal_password'
        # Required to load the user profile page because of the key-value fields
        create_group(PROFILE_GROUP)

    def _login(self, name, password):
        """Generic login handler"""
        login_url = reverse('auth_login')
        self.driver.get(f"{self.live_server_url}{login_url}")
        WebDriverWait(self.driver, WAIT_TIME).until(
            expected_conditions.presence_of_element_located((By.NAME, "submit"))
        )
        user_field = self.driver.find_element(By.NAME, 'username')
        user_field.send_keys(name)
        pass_field = self.driver.find_element(By.NAME, 'password')
        pass_field.send_keys(password)
        loginbut = self.driver.find_element(By.NAME, 'submit')
        loginbut.click()
        WebDriverWait(self.driver, WAIT_TIME).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, "wafer-profile"))
        )

    def normal_login(self):
        """Login as an ordinary user"""
        self._login(self.normal_user.username, self.normal_password)

    def admin_login(self):
        """Login as the admin user"""
        self._login(self.admin_user.username, self.admin_password)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()


@tag('chrome')
class ChromeTestRunner(BaseWebdriverRunner):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Load the chrome webdriver
        cls.options = webdriver.ChromeOptions()
        cls.options.add_argument("--headless=new")
        cls.driver = webdriver.Chrome(options=cls.options)


@tag('firefox')
class FirefoxTestRunner(BaseWebdriverRunner):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Load the firefox webdriver
        cls.options = webdriver.FirefoxOptions()
        cls.options.add_argument('-headless')
        # Disable options that may break selenium
        # see https://github.com/mozilla/geckodriver/releases/tag/v0.33.0 and
        # https://github.com/SeleniumHQ/selenium/issues/11736
        cls.options.set_preference('fission.bfcacheInParent', False)
        cls.options.set_preference('fission.webContentIsolationStrategy', 0)
        cls.driver = webdriver.Firefox(options=cls.options)
