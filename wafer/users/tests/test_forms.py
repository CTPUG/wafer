"""Test user profile forms, especially the content influenced by settings"""

from django.test import Client, TestCase
from django.core.exceptions import ValidationError
from wafer.users.profile_urls import make_profile_field, render_profile_url
from wafer.tests.utils import create_group, create_user
from wafer.users.models import PROFILE_GROUP
from wafer.kv.models import KeyValue


def validate_test_username(value):
    if not value.isalnum():
        raise ValidationError("Use letters and numbers only.")


def render_test_github_username(value):
    return f"https://github.com/{value}"


class UserProfileFormContentTests(TestCase):

    def setUp(self):
        self.user1 = create_user('test1')
        self.group = create_group(PROFILE_GROUP)
        self.client = Client()

    def test_custom_profile_validation_and_rendering(self):
        with self.settings(
            CODE_HOSTING_VALIDATORS={
                "github": "wafer.users.tests.test_forms.validate_test_username",
            },
            CODE_HOSTING_RENDERERS={
                "github": "wafer.users.tests.test_forms.render_test_github_username",
            },
        ):
            field = make_profile_field("CODE_HOSTING", "github", "GitHub")
            self.assertEqual(field.clean("olabodeIdowu"), "olabodeIdowu")

            with self.assertRaises(ValidationError):
                field.clean("invalid-name!")

            self.assertEqual(
                render_profile_url("CODE_HOSTING", "github", "olabodeIdowu"),
                "https://github.com/olabodeIdowu",
            )

    def test_entires(self):
        """Test that all the fields in the settings show up as expected"""
        self.client.login(username='test1', password='test1_password')
        with self.settings(CODE_HOSTING_ENTRIES={'gitlab': 'GitLab', 'github': 'GitHub'},
                           SOCIAL_MEDIA_ENTRIES={'twitter': 'Twitter', 'fedivere': 'Fediverse'}):
            form = self.client.get('/users/test1/edit_profile/').content
            self.assertTrue(b'Twitter' in form)
            self.assertTrue(b'Fediverse' in form)
            self.assertTrue(b'GitLab' in form)
            self.assertTrue(b'GitHub' in form)

        # Test with a reduced set
        with self.settings(CODE_HOSTING_ENTRIES={'gitlab': 'GitLab'},
                           SOCIAL_MEDIA_ENTRIES={'twitter': 'Twitter'}):
            form = self.client.get('/users/test1/edit_profile/').content
            self.assertTrue(b'Twitter' in form)
            self.assertTrue(b'Fediverse' not in form)
            self.assertTrue(b'GitLab' in form)
            self.assertTrue(b'GitHub' not in form)

    def test_save(self):
        """Test that saving a form adds the data correctly"""
        self.client.login(username='test1', password='test1_password')
        with self.settings(CODE_HOSTING_ENTRIES={'gitlab': 'GitLab', 'github': 'GitHub'},
                           SOCIAL_MEDIA_ENTRIES={'twitter': 'Twitter', 'fediverse': 'Fediverse'}):
            self.client.post('/users/test1/edit_profile/',
                data={'bio': 'A bio',
                      'twitter': 'https://twitter.com/test',
                      'fediverse': 'https://myserver.test/test',
                      'github': 'https://github.com/test'})
            self.assertEqual(KeyValue.objects.filter(group=self.group, key='twitter').count(), 1)
            self.assertEqual(KeyValue.objects.filter(group=self.group, key='fediverse').count(), 1)
            self.assertEqual(KeyValue.objects.filter(group=self.group, key='github').count(), 1)
            self.assertEqual(KeyValue.objects.filter(group=self.group, key='gitlab').count(), 1)

            kv = KeyValue.objects.filter(group=self.group, key='twitter').get()
            self.assertEqual(kv.value, 'https://twitter.com/test')
            kv = KeyValue.objects.filter(group=self.group, key='github').get()
            self.assertEqual(kv.value, 'https://github.com/test')
            kv = KeyValue.objects.filter(group=self.group, key='fediverse').get()
            self.assertEqual(kv.value, 'https://myserver.test/test')

            # Test that the social profiles can be removed
            self.client.post('/users/test1/edit_profile/',
                data={'twitter': '',
                      'fediverse': '',
                      'github': ''})

            kv = KeyValue.objects.filter(group=self.group, key='twitter').get()
            self.assertEqual(kv.value, '')
            kv = KeyValue.objects.filter(group=self.group, key='github').get()
            self.assertEqual(kv.value, '')
            kv = KeyValue.objects.filter(group=self.group, key='fediverse').get()
            self.assertEqual(kv.value, '')
