"""Test user profile forms, especially the content influenced by settings"""

from django.test import Client, TestCase
from wafer.tests.utils import create_group, create_user
from wafer.users.models import PROFILE_GROUP
from wafer.kv.models import KeyValue


class UserProfileFormContentTests(TestCase):

    def setUp(self):
        self.user1 = create_user('test1')
        self.group = create_group(PROFILE_GROUP)
        self.client = Client()

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
            self.assertEqual(KeyValue.objects.filter(group=self.group, key='gitlab').count(), 0)

            kv = KeyValue.objects.filter(group=self.group, key='twitter').get()
            self.assertEqual(kv.value, 'https://twitter.com/test')
            kv = KeyValue.objects.filter(group=self.group, key='github').get()
            self.assertEqual(kv.value, 'https://github.com/test')
            kv = KeyValue.objects.filter(group=self.group, key='fediverse').get()
            self.assertEqual(kv.value, 'https://myserver.test/test')
