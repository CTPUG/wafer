# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
"""Tests for wafer.user.views"""

import mock

from django.test import Client, TestCase

from wafer.users.models import PROFILE_GROUP
from wafer.talks.models import ACCEPTED
from wafer.talks.tests.fixtures import create_talk
from wafer.tests.utils import create_group, create_user, mock_avatar_url


class UserProfilePermissionTests(TestCase):
    """Tests the various permission models for the profile view"""

    def setUp(self):
        # Create 2 users
        create_user('test1')
        create_user('test2')
        # create kv group
        create_group(PROFILE_GROUP)
        # And a 3rd, with a talk
        create_talk(title="Test talk", status=ACCEPTED, username='test3')
        self.client = Client()

    @mock.patch('wafer.users.models.UserProfile.avatar_url', mock_avatar_url)
    def test_not_logged_in_private_userlist(self):
        """We should get 403 for both existing and non-existant users.

           We can see the user with the accepted talk."""
        with self.settings(WAFER_PUBLIC_ATTENDEE_LIST=False):
            response = self.client.get('/users/test1/')
            self.assertEqual(response.status_code, 403)
            response = self.client.get('/users/test1/edit_profile/')
            self.assertEqual(response.status_code, 403)

            response = self.client.get('/users/test2/')
            self.assertEqual(response.status_code, 403)
            response = self.client.get('/users/test2/edit_profile/')
            self.assertEqual(response.status_code, 403)

            response = self.client.get('/users/test3/')
            self.assertEqual(response.status_code, 200)
            response = self.client.get('/users/test3/edit_profile/')
            self.assertEqual(response.status_code, 403)

            response = self.client.get('/users/does_not_exist/')
            self.assertEqual(response.status_code, 403)
            response = self.client.get('/users/does_not_exist/edit_profile/')
            self.assertEqual(response.status_code, 403)

    @mock.patch('wafer.users.models.UserProfile.avatar_url', mock_avatar_url)
    def test_logged_in_private_userlist(self):
        """We can see and edit our own profile, but get 403's for existing and
           non-existing users.

           We can see the user with an accepted talk, but not edit."""
        self.client.login(username='test1', password="test1_password")
        with self.settings(WAFER_PUBLIC_ATTENDEE_LIST=False):
            response = self.client.get('/users/test1/')
            self.assertEqual(response.status_code, 200)
            response = self.client.get('/users/test1/edit_profile/')
            self.assertEqual(response.status_code, 200)

            response = self.client.get('/users/test2/')
            self.assertEqual(response.status_code, 403)
            response = self.client.get('/users/test2/edit_profile/')
            self.assertEqual(response.status_code, 403)

            response = self.client.get('/users/test3/')
            self.assertEqual(response.status_code, 200)
            response = self.client.get('/users/test3/edit_profile/')
            self.assertEqual(response.status_code, 403)

            response = self.client.get('/users/does_not_exist/')
            self.assertEqual(response.status_code, 403)
            response = self.client.get('/users/does_not_exist/edit_profile/')
            self.assertEqual(response.status_code, 403)

    @mock.patch('wafer.users.models.UserProfile.avatar_url', mock_avatar_url)
    def test_not_logged_in_public_userlist(self):
        """We should be able to access profiles, but not edit them.

           we should get 404's for non-existing users and other bits
           we can't access."""
        with self.settings(WAFER_PUBLIC_ATTENDEE_LIST=True):
            response = self.client.get('/users/test1/')
            self.assertEqual(response.status_code, 200)
            response = self.client.get('/users/test1/edit_profile/')
            self.assertEqual(response.status_code, 404)

            response = self.client.get('/users/test2/')
            self.assertEqual(response.status_code, 200)
            response = self.client.get('/users/test2/edit_profile/')
            self.assertEqual(response.status_code, 404)

            response = self.client.get('/users/test3/')
            self.assertEqual(response.status_code, 200)
            response = self.client.get('/users/test3/edit_profile/')
            self.assertEqual(response.status_code, 404)

            response = self.client.get('/users/does_not_exist/')
            self.assertEqual(response.status_code, 404)
            response = self.client.get('/users/does_not_exist/edit_profile/')
            self.assertEqual(response.status_code, 404)

    @mock.patch('wafer.users.models.UserProfile.avatar_url', mock_avatar_url)
    def test_logged_in_pulic_userlist(self):
        """We should be able to edit our profile.
           We should be able to access other profiles, but not edit them.

           we should get 404's for non-existing users."""
        self.client.login(username='test1', password="test1_password")
        with self.settings(WAFER_PUBLIC_ATTENDEE_LIST=True):
            response = self.client.get('/users/test1/')
            self.assertEqual(response.status_code, 200)
            response = self.client.get('/users/test1/edit_profile/')
            self.assertEqual(response.status_code, 200)

            response = self.client.get('/users/test2/')
            self.assertEqual(response.status_code, 200)
            response = self.client.get('/users/test2/edit_profile/')
            self.assertEqual(response.status_code, 404)

            response = self.client.get('/users/test3/')
            self.assertEqual(response.status_code, 200)
            response = self.client.get('/users/test3/edit_profile/')
            self.assertEqual(response.status_code, 404)

            response = self.client.get('/users/does_not_exist/')
            self.assertEqual(response.status_code, 404)
            response = self.client.get('/users/does_not_exist/edit_profile/')
            self.assertEqual(response.status_code, 404)


class UserProfileViewTests(TestCase):
    """Test the dynamic content influence by settings"""

    def setUp(self):
        # Create 2 users
        user1 = create_user('test1')
        user2 = create_user('test2')
        # create kv group
        group = create_group(PROFILE_GROUP)
        self.client = Client()

        # Create some entries
        user1.userprofile.kv.get_or_create(group=group, key='github',
                defaults={'value': 'https://github.com/aaa'})
        user1.userprofile.kv.get_or_create(group=group, key='gitlab',
                defaults={'value': 'https://gitlab.com/aaa'})
        user1.userprofile.kv.get_or_create(group=group, key='twitter',
                defaults={'value': 'https://twitter.com/aaa'})
        user1.userprofile.kv.get_or_create(group=group, key='fediverse',
                defaults={'value': 'https://myserver.org/fediverse/aaa'})
        user2.userprofile.kv.get_or_create(group=group, key='github',
                defaults={'value': 'https://github.com/bbb'})
        user2.userprofile.kv.get_or_create(group=group, key='twitter',
                defaults={'value': 'https://twitter.com/bbb'})

    @mock.patch('wafer.users.models.UserProfile.avatar_url', mock_avatar_url)
    def test_social_entries(self):
        # Test that we see the expected results with the default setting
        user1_view = self.client.get('/users/test1/').content
        self.assertTrue(b'https://twitter.com/aaa' in user1_view)
        self.assertTrue(b'https://myserver.org/fediverse/aaa' in user1_view)
        self.assertTrue(b'https://twitter.com/bbb' not in user1_view)

        user2_view = self.client.get('/users/test2/').content
        self.assertTrue(b'https://twitter.com/bbb' in user2_view)
        self.assertTrue(b'https://twitter.com/aaa' not in user2_view)
        # Test that removing twitter from the settings results in it not being rendered,
        with self.settings(SOCIAL_MEDIA_ENTRIES={'fediverse': 'Fediverse'}):
            user1_view = self.client.get('/users/test1/').content
            self.assertTrue(b'https://twitter.com/aaa' not in user1_view)
            self.assertTrue(b'https://myserver.org/fediverse/aaa' in user1_view)

            user2_view = self.client.get('/users/test2/').content
            self.assertTrue(b'https://twitter.com/bbb' not in user2_view)

    @mock.patch('wafer.users.models.UserProfile.avatar_url', mock_avatar_url)
    def test_code_entries(self):
        user1_view = self.client.get('/users/test1/').content
        self.assertTrue(b'https://github.com/aaa' in user1_view)
        self.assertTrue(b'https://gitlab.com/aaa' in user1_view)
        self.assertTrue(b'https://github.com/bbb' not in user1_view)

        user2_view = self.client.get('/users/test2/').content
        self.assertTrue(b'https://github.com/bbb' in user2_view)
        self.assertTrue(b'https://github.com/aaa' not in user2_view)
        # Test that removing twitter from the settings results in it not being rendered,
        with self.settings(CODE_HOSTING_ENTRIES={'gitlab': 'GitLab'}):
            user1_view = self.client.get('/users/test1/').content
            self.assertTrue(b'https://github.com/aaa' not in user1_view)
            self.assertTrue(b'https://gitlab.com/aaa' in user1_view)

            user2_view = self.client.get('/users/test2/').content
            self.assertTrue(b'https://github.com/bbb' not in user2_view)
