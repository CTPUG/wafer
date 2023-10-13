"""Basic tests for the SSO behaviour

These tests mock out the actual SSO interactions and only
test that accounts are created correctly and some of the
error paths"""


import mock

from django.test import TestCase
from django.contrib.auth import get_user_model

from wafer.tests.utils import create_group, create_user

from wafer.registration.sso import github_sso, gitlab_sso, SSOError
from wafer.kv.models import KeyValue


# Helper classes for mocking request calls
class SSOPost:

    def __init__(self, status_code, access_token):
        self.status_code = status_code
        self.access_token = access_token

    def json(self):
        return {'access_token': self.access_token}

class SSOGet:

    def __init__(self, status_code, username, name, email):
        self.status_code = status_code
        self.username = username
        self.name = name
        self.email = email

    def json(self):
        # We duplicate username, id and login so we can use this for
        # both gitlab and github
        json = {
            'login': self.username,
            'username': self.username,
            'id': self.username,
            'name': self.name,
        }
        # We allow a null email address to remove the field for
        # testing error cases
        if self.email:
            json['email'] = self.email
        return json


class RegistrationSSOTests(TestCase):

    def setUp(self):
        self.reg_group = create_group('Registration')

    @mock.patch('requests.post', new=lambda x, **kw: SSOPost(status_code=200, access_token='aaaa'))
    @mock.patch('requests.get', new=lambda x, **kw: SSOGet(status_code=200, username='joe',
                                                          name='Joe Soap', email='joe@nowhere.test'))
    def test_github_success(self):
        """Test that a successful github auth call creates the user and
           sets the right values"""
        # Check that no user currently exists
        self.assertEqual(get_user_model().objects.filter(username='joe').count(), 0)
        with self.settings(WAFER_GITHUB_CLIENT_ID='testy', WAFER_GITHUB_CLIENT_SECRET='abc'):
            user = github_sso('abcde')
        self.assertEqual(user.username, 'joe')
        self.assertEqual(user.first_name, 'Joe')
        self.assertEqual(user.last_name, 'Soap')
        self.assertEqual(user.email, 'joe@nowhere.test')

        kv = KeyValue.objects.filter(group=self.reg_group, key="github_sso_account_id").get()
        self.assertEqual(kv.value, user.username)

        # Check that calling this again gives the same user back
        with self.settings(WAFER_GITHUB_CLIENT_ID='testy', WAFER_GITHUB_CLIENT_SECRET='abc'):
            user2 = github_sso('abcde')

        self.assertEqual(user, user2)
        # Check we only created 1 user
        self.assertEqual(get_user_model().objects.filter(username='joe').count(), 1)

    def test_github_fail(self):
        """Test that a failed github auth call doesn't create a user"""
        # Test incorrect code response
        cur_users = get_user_model().objects.count()
        with (self.assertRaises(SSOError) as cm,
                self.settings(WAFER_GITHUB_CLIENT_ID='testy', WAFER_GITHUB_CLIENT_SECRET='abc'),
                mock.patch('requests.post', new=lambda x, **kw: SSOPost(status_code=333, access_token='aaaa'))):
            user = github_sso('abcde')
        self.assertTrue('Invalid code' in str(cm.exception))
        self.assertEqual(cur_users, get_user_model().objects.count())

        # Test auth token response failure
        with (self.assertRaises(SSOError) as cm,
                self.settings(WAFER_GITHUB_CLIENT_ID='testy', WAFER_GITHUB_CLIENT_SECRET='abc'),
                mock.patch('requests.post', new=lambda x, **kw: SSOPost(status_code=200, access_token='aaaa')),
                mock.patch('requests.get', new=lambda x, **kw: SSOGet(status_code=333, username='github_dup',
                                                                      name='Joe Soap', email='joe@nowhere.test'))):
            user = github_sso('abcde')
        self.assertTrue('Failed response from GitHub' in str(cm.exception))
        self.assertEqual(cur_users, get_user_model().objects.count())

    @mock.patch('requests.post', new=lambda x, **kw: SSOPost(status_code=200, access_token='aaaa'))
    @mock.patch('requests.get', new=lambda x, **kw: SSOGet(status_code=200, username='github_dup',
                                                           name='Joe Soap', email='joe@nowhere.test'))
    def test_github_duplicate(self):
        """Test that we get the expected error message if someone tries
           to reuse the github username for sso"""
        # This tests multiple KeyValues with the same data
        dup1 = create_user('github_dup1')
        dup1.userprofile.kv.get_or_create(group=self.reg_group,
                                          key='github_sso_account_id',
                                          defaults={'value': 'github_dup'})
        dup2 = create_user('github_dup2')
        dup2.userprofile.kv.get_or_create(group=self.reg_group,
                                          key='github_sso_account_id',
                                          defaults={'value': 'github_dup'})
        with (self.assertRaises(SSOError) as cm, self.settings(WAFER_GITHUB_CLIENT_ID='testy', WAFER_GITHUB_CLIENT_SECRET='abcd')):
            user = github_sso('abcdef')
        exception = cm.exception
        self.assertTrue('Multiple accounts have the same GitHub' in str(exception))

    @mock.patch('requests.post', new=lambda x, **kw: SSOPost(status_code=200, access_token='aaaa'))
    @mock.patch('requests.get', new=lambda x, **kw: SSOGet(status_code=200, username='joe2',
                                                           name='Joe2 Soap', email='joe2@nowhere.test'))
    def test_gitlab_success(self):
        """Test that a successful gitlab auth call creates the user and
           sets the right values"""
        # Check that no user currently exists
        self.assertEqual(get_user_model().objects.filter(username='joe2').count(), 0)
        with self.settings(WAFER_GITLAB_CLIENT_ID='testy', WAFER_GITLAB_CLIENT_SECRET='abc'):
            user = gitlab_sso('abcde', 'http://localhost/')
        self.assertEqual(user.username, 'joe2')
        self.assertEqual(user.first_name, 'Joe2')
        self.assertEqual(user.last_name, 'Soap')
        self.assertEqual(user.email, 'joe2@nowhere.test')

        kv = KeyValue.objects.filter(group=self.reg_group, key="gitlab_sso_account_id").get()
        self.assertEqual(kv.value, user.username)

        # Check that calling this again gives the same user back
        with self.settings(WAFER_GITLAB_CLIENT_ID='testy', WAFER_GITLAB_CLIENT_SECRET='abc'):
            user2 = gitlab_sso('abcde', 'http://localhost/')

        self.assertEqual(user, user2)
        # Check we only created 1 user
        self.assertEqual(get_user_model().objects.filter(username='joe2').count(), 1)

    def test_gitlab_fail(self):
        """Test that a failed gitlab auth call doesn't create a user"""
        # Test incorrect code response
        cur_users = get_user_model().objects.count()
        with (self.assertRaises(SSOError) as cm,
                self.settings(WAFER_GITLAB_CLIENT_ID='testy', WAFER_GITLAB_CLIENT_SECRET='abc'),
                mock.patch('requests.post', new=lambda x, **kw: SSOPost(status_code=333, access_token='aaaa'))):
            user = gitlab_sso('abcde', 'http://localhost/')
        self.assertTrue('Invalid code' in str(cm.exception))
        self.assertEqual(cur_users, get_user_model().objects.count())

        # Test auth token response failure
        with (self.assertRaises(SSOError) as cm,
                self.settings(WAFER_GITLAB_CLIENT_ID='testy', WAFER_GITLAB_CLIENT_SECRET='abc'),
                mock.patch('requests.post', new=lambda x, **kw: SSOPost(status_code=200, access_token='aaaa')),
                mock.patch('requests.get', new=lambda x, **kw: SSOGet(status_code=333, username='github_dup',
                                                                      name='Joe Soap', email='joe@nowhere.test'))):
            user = gitlab_sso('abcde', 'http://localhost/')
        self.assertTrue('Failed response from GitLab' in str(cm.exception))
        self.assertEqual(cur_users, get_user_model().objects.count())
        # Test profile error
        with (self.assertRaises(SSOError) as cm,
                self.settings(WAFER_GITLAB_CLIENT_ID='testy', WAFER_GITLAB_CLIENT_SECRET='abc'),
                mock.patch('requests.post', new=lambda x, **kw: SSOPost(status_code=200, access_token='aaaa')),
                mock.patch('requests.get', new=lambda x, **kw: SSOGet(status_code=200, username='github_dup',
                                                                      name='Joe Soap', email=None))):
            user = gitlab_sso('abcde', 'http://localhost/')
        self.assertEqual('GitLab profile missing required content', str(cm.exception))
        self.assertEqual(cur_users, get_user_model().objects.count())

    @mock.patch('requests.post', new=lambda x, **kw: SSOPost(status_code=200, access_token='aaaa'))
    @mock.patch('requests.get', new=lambda x, **kw: SSOGet(status_code=200, username='dup2',
                                                           name='Joe2 Soap', email='joe2@nowhere.test'))
    def test_gitlab_duplicate(self):
        """Test that we get the expected error message if someone tries
           to reuse the gitlab username for sso"""
        # Thi tests mulitple users sharing a single KeyValue entry
        dup1 = create_user('gitlab_dup1')
        dup1.userprofile.kv.get_or_create(group=self.reg_group,
                                          key='gitlab_sso_account_id',
                                          defaults={'value': 'dup2'})
        dup2 = create_user('gitlab_dup2')
        kv = KeyValue.objects.filter(group=self.reg_group, key='gitlab_sso_account_id', value='dup2').get()
        kv.userprofile_set.add(dup2.userprofile)
        with (self.assertRaises(SSOError) as cm, self.settings(WAFER_GITLAB_CLIENT_ID='testy', WAFER_GITLAB_CLIENT_SECRET='abcd')):
            gitlab_sso('abcdef', 'http://localhost/')
        exception = cm.exception
        self.assertTrue('Multiple accounts have GitLab' in str(exception))

