# This tests the basic compare list, to ensure it's working as expected

from django.contrib.auth import get_user_model
from django.utils.timezone import datetime, now

from django.test import Client, TestCase

from reversion import revisions

from wafer.talks.models import Talk, TalkType, SUBMITTED
from wafer.talks.tests.fixtures import create_talk
from wafer.tests.utils import create_user


class TestBasicCompareList(TestCase):
    """Basic talk tests"""

    def setUp(self):
        """Setup a user with a talk"""
        talk_user = create_user('john')
        self.super = create_user('super', superuser=True)
        self.talk_a = create_talk('This is a test talk', status=SUBMITTED, user=talk_user)
        # Create a base revision
        with revisions.create_revision():
            self.talk_a.save()
        # Edit 1
        self.talk_a.abstract = "This is an abstract"
        with revisions.create_revision():
            self.talk_a.save()
        self.talk_a.abstract = "This is not an abstract"
        with revisions.create_revision():
            self.talk_a.save()
        self.client = Client()

    def test_get_compare_list(self):
        """Get the compare list and check the number of entries"""
        self.client.login(username="super", password="super_password")
        response = self.client.get(f'/admin/talks/talk/{self.talk_a.pk}/comparelist/')
        # Check we have 3 revisions to compare
        self.assertIn(b'/1/compare', response.content)
        self.assertIn(b'/2/compare', response.content)
        self.assertIn(b'/3/compare', response.content)
        # Check that we don't have unexpcted ones
        self.assertNotIn(b'/4/compare', response.content)

    def test_get_diffs(self):
        """Check that diffs look sensible"""
        self.client.login(username="super", password="super_password")
        response = self.client.get(f'/admin/talks/talk/{self.talk_a.pk}/2/compare/')
        # Check that the 'not' we added is marked
        # This should maybe a regex to avoid assumptions about the whitespace
        # positioning.
        self.assertIn(b'>not </ins>', response.content)
