"""Tests for wafer.kv api views."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.test import APIClient
from wafer.kv.models import KeyValue
from wafer.talks.models import Talk
import json


def get_group(group):
    return Group.objects.get(name=group)


def create_group(group):
    return Group.objects.create(name=group)


def create_user(username, groups, superuser=False):
    if superuser:
        create = get_user_model().objects.create_superuser
    else:
        create = get_user_model().objects.create_user
    user = create(
        username, '%s@example.com' % username, 'password')
    for the_group in groups:
        grp = get_group(the_group)
        user.groups.add(grp)
    user.save()
    return user


def create_talk(title, user, kv_pairs):
    talk = Talk.objects.create(
        title=title, corresponding_author_id=user.id)
    talk.authors.add(user)
    for pair in kv_pairs:
        talk.kv.add(pair)
    talk.abstract = 'An abstract'
    talk.save()
    return talk


def create_kv_pair(name, value, group):
    group = get_group(group)
    return KeyValue.objects.create(key=name, value=value, group=group)


class KeyValueViewSetTests(TestCase):
    """Various tests of the API views."""

    def setUp(self):
        for grp in ['group_1', 'group_2', 'group_3', 'group_4']:
            create_group(grp)
        self.user1 = create_user("user1", ["group_1", "group_2"])
        self.superuser = create_user("super", ["group_1", "group_2"], True)
        self.user2 = create_user("user2", ["group_1"])
        self.user3 = create_user("user3", ["group_4"])
        self.user4 = create_user("user4", ["group_3"])
        self.kv_1_grp1 = create_kv_pair("Val 1.1", '{"key": "Data"}', "group_1")
        self.kv_2_grp2 = create_kv_pair("Val 2.1", '{"key2": "False"}', "group_2")
        self.kv_2_grp1 = create_kv_pair("Val 1.2", '{"key3": "True"}', "group_1")
        self.kv_3_grp1 = create_kv_pair("Val 1.3", '{"key1": "Data"}', "group_1")
        self.kv_3_grp3 = create_kv_pair("Val 3.1", '{"key1": "Data"}', "group_3")
        self.duplicate_name = create_kv_pair("Val 1.1", '{"key1": "Data"}', "group_3")
        self.client = APIClient()

    def test_unauthorized_users(self):
        response = self.client.get('/kv/api/kv/')
        self.assertEqual(response.data['count'], 0)
        response = self.client.get('/kv/api/kv/%d/' % self.kv_1_grp1.pk)
        self.assertEqual(response.status_code, 404)

    def test_group_1_member(self):
        self.client.login(username='user2', password='password')
        response = self.client.get('/kv/api/kv/')
        self.assertEqual(response.data['count'], 3)
        pairs = [x['key'] for x in response.data['results']]
        self.assertTrue('Val 1.1' in pairs)
        self.assertTrue('Val 1.2' in pairs)
        self.assertTrue('Val 1.3' in pairs)
        response = self.client.get('/kv/api/kv/%d/' % self.kv_1_grp1.pk)
        self.assertEqual(response.data['key'], 'Val 1.1')
        response = self.client.get('/kv/api/kv/%d/' % self.kv_2_grp1.pk)
        self.assertEqual(response.data['key'], 'Val 1.2')
        response = self.client.get('/kv/api/kv/%d/' % self.kv_2_grp2.pk)
        self.assertEqual(response.status_code, 404)

    def test_group_1_2_member(self):
        self.client.login(username='user1', password='password')
        response = self.client.get('/kv/api/kv/')
        self.assertEqual(response.data['count'], 4)
        pairs = [x['key'] for x in response.data['results']]
        self.assertTrue('Val 1.1' in pairs)
        self.assertTrue('Val 1.2' in pairs)
        self.assertTrue('Val 1.3' in pairs)
        self.assertTrue('Val 2.1' in pairs)
        response = self.client.get('/kv/api/kv/%d/' % self.kv_1_grp1.pk)
        self.assertEqual(response.data['key'], 'Val 1.1')
        response = self.client.get('/kv/api/kv/%d/' % self.kv_2_grp1.pk)
        self.assertEqual(response.data['key'], 'Val 1.2')
        response = self.client.get('/kv/api/kv/%d/' % self.kv_2_grp2.pk)
        self.assertEqual(response.data['key'], 'Val 2.1')
        response = self.client.get('/kv/api/kv/%d/' % self.kv_3_grp3.pk)
        self.assertEqual(response.status_code, 404)

    def test_group_4_member(self):
        self.client.login(username='user3', password='password')
        response = self.client.get('/kv/api/kv/')
        self.assertEqual(response.data['count'], 0)
        response = self.client.get('/kv/api/kv/%d/' % self.kv_1_grp1.pk)
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/kv/api/kv/%d/' % self.kv_2_grp2.pk)
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/kv/api/kv/%d/' % self.kv_3_grp3.pk)
        self.assertEqual(response.status_code, 404)

    def test_group_3_member(self):
        self.client.login(username='user4', password='password')
        response = self.client.get('/kv/api/kv/')
        self.assertEqual(response.data['count'], 2)
        pairs = [x['key'] for x in response.data['results']]
        self.assertTrue('Val 1.1' in pairs)
        self.assertTrue('Val 3.1' in pairs)
        response = self.client.get('/kv/api/kv/%d/' % self.kv_3_grp3.pk)
        self.assertEqual(response.data['key'], 'Val 3.1')
        response = self.client.get('/kv/api/kv/%d/' % self.duplicate_name.pk)
        self.assertEqual(response.data['key'], 'Val 1.1')
        response = self.client.get('/kv/api/kv/%d/' % self.kv_1_grp1.pk)
        self.assertEqual(response.status_code, 404)

    def test_kv_talks(self):
        """Check that talks are shown added to the corresponding API
           view."""
        self.client.login(username='user1', password='password')
        talk1 = create_talk('A talk', self.user1,
                            [self.kv_1_grp1, self.kv_2_grp2])
        talk2 = create_talk('Another talk', self.user1,
                            [self.kv_2_grp1, self.kv_2_grp2, self.kv_3_grp3])
        # Check we have the correct number of talks when we query on the keys
        response = self.client.get('/kv/api/kv/%d/' % self.kv_1_grp1.pk)
        self.assertEqual(len(response.data['talk']), 1)
        response = self.client.get('/kv/api/kv/%d/' % self.kv_2_grp2.pk)
        self.assertEqual(len(response.data['talk']), 2)
        # Check we can follow the url in the response
        talk_response = self.client.get(response.data['talk'][0])
        self.assertEqual(talk_response.data['title'], 'A talk')
        self.assertEqual(len(talk_response.data['kv']), 2)
        # We use substring tests to avoiding needing to construct the full url.
        kv_pairs = '\n'.join(talk_response.data['kv'])
        self.assertTrue('/kv/api/kv/%d/' % self.kv_1_grp1.pk in kv_pairs)
        self.assertTrue('/kv/api/kv/%d/' % self.kv_2_grp2.pk in kv_pairs)
        # Check that kv pairs we can't access are hidden in the talk request
        talk_url = response.data['talk'][1]
        talk_response = self.client.get(talk_url)
        self.assertEqual(talk_response.data['title'], 'Another talk')
        self.assertEqual(len(talk_response.data['kv']), 3)
        kv_pairs = '\n'.join(talk_response.data['kv'])
        self.assertTrue('/kv/api/kv/%d/' % self.kv_2_grp1.pk in kv_pairs)
        self.assertTrue('/kv/api/kv/%d/' % self.kv_2_grp2.pk in kv_pairs)
        self.assertTrue('hidden' in kv_pairs)
        # Check changing kv's via the talk request
        # Need to be a super user due to the talk view permissions
        self.client.login(username='super', password='password')
        kv_urls = [x for x in talk_response.data['kv'] if 'hidden' not in x]
        data = talk_response.data.copy()
        data['kv'] = [x for x in kv_urls
                      if '/kv/api/kv/%d/' % self.kv_2_grp1.pk in x]
        talk_response = self.client.put(talk_url, data, format='json')
        self.assertEqual(talk_response.status_code, 200)
        talk_response = self.client.get(talk_url)
        self.assertEqual(talk_response.data['title'], 'Another talk')
        self.assertEqual(len(talk_response.data['kv']), 2)
        kv_pairs = '\n'.join(talk_response.data['kv'])
        self.assertTrue('/kv/api/kv/%d/' % self.kv_2_grp1.pk in kv_pairs)
        data = {'kv': []}
        talk_response = self.client.patch(talk_url, data, format='json')
        self.assertEqual(talk_response.status_code, 200)
        talk_response = self.client.get(talk_url)
        self.assertEqual(talk_response.data['title'], 'Another talk')
        self.assertEqual(len(talk_response.data['kv']), 1)
        kv_pairs = '\n'.join(talk_response.data['kv'])
        self.assertTrue('hidden' in kv_pairs)
        # Check adding kv values back
        data = {'kv': kv_urls}
        talk_response = self.client.patch(talk_url, data, format='json')
        self.assertEqual(talk_response.status_code, 200)
        talk_response = self.client.get(talk_url)
        self.assertEqual(talk_response.data['title'], 'Another talk')
        self.assertEqual(len(talk_response.data['kv']), 3)
        kv_pairs = '\n'.join(talk_response.data['kv'])
        self.assertTrue('hidden' in kv_pairs)
        self.assertTrue(kv_urls[0] in kv_pairs)
        self.assertTrue(kv_urls[1] in kv_pairs)


class KeyValueAPITests(TestCase):
    """Test creating, updating and deleting via the api."""

    def setUp(self):
        for grp in ['group_1', 'group_2']:
            create_group(grp)
        self.user1 = create_user("user1", ["group_1", "group_2"])
        self.user2 = create_user("user2", ["group_1"]),
        self.user3 = create_user("user3", ["group_2"]),
        self.kv_1_grp1 = create_kv_pair("Val 1.1", '{"key": "Data"}', "group_1")
        self.kv_2_grp2 = create_kv_pair("Val 2.1", '{"key2": "False"}', "group_2")
        self.kv_3_grp1 = create_kv_pair("Val 1.3", '{"key1": "Data"}', "group_1")
        self.client = APIClient()

    def test_group_1_actions(self):
        self.client.login(username='user2', password='password')
        # Test creation
        data = {'key': 'new',
                'value': "{'mykey': 'Value'}",
                'group': get_group("group_1").pk}
        response = self.client.post('/kv/api/kv/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(KeyValue.objects.filter(key="new").exists())
        kv = KeyValue.objects.get(key='new')
        self.assertEqual(kv.value, "{'mykey': 'Value'}")
        # Test update
        data = {'value': "{'mykey': 'Value 2'}"}
        response = self.client.patch('/kv/api/kv/%d/' % kv.pk, data,
                                     format='json')
        self.assertEqual(response.status_code, 200)
        kv = KeyValue.objects.get(key='new')
        self.assertEqual(kv.value, "{'mykey': 'Value 2'}")

        self.client.login(username='user1', password='password')
        # Test that changing group ownership fails
        data = {'group': get_group("group_2").pk}
        response = self.client.patch('/kv/api/kv/%d/' % kv.pk, data,
                                     format='json')
        self.assertEqual(response.status_code, 403)
        # Test deletion
        response = self.client.delete('/kv/api/kv/%d/' % kv.pk)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(KeyValue.objects.filter(key="new").exists())

        # Test non-group member
        self.client.login(username='user3', password='password')
        response = self.client.delete('/kv/api/kv/%d/' % self.kv_1_grp1.pk)
        self.assertEqual(response.status_code, 404)
        data = {'key': 'foobar'}
        response = self.client.patch('/kv/api/kv/%d/' % self.kv_1_grp1.pk, data,
                                     format='json')
        self.assertEqual(response.status_code, 404)
        # Test that we can't create keys outside our group
        data = {'key': 'new',
                'value': "{'mykey': 'Value'}",
                'group': get_group("group_1").pk}
        response = self.client.post('/kv/api/kv/', data, format='json')
        self.assertEqual(response.status_code, 400)


    def test_group_2_actions(self):
        # Same tests as above, but with group_2 and a different ordering
        # of users belonging to 1 or both groups
        # Multi-group user
        self.client.login(username='user1', password='password')
        data = {'key': 'new',
                'value': "{'mykey': 'Value'}",
                'group': get_group("group_2").pk}
        response = self.client.post('/kv/api/kv/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(KeyValue.objects.filter(key="new").exists())
        kv = KeyValue.objects.get(key='new')
        self.assertEqual(kv.value, "{'mykey': 'Value'}")
        # Single group user
        self.client.login(username='user3', password='password')
        data = {'value': "{'mykey': 'Value 2'}"}
        response = self.client.patch('/kv/api/kv/%d/' % kv.pk, data,
                                     format='json')
        self.assertEqual(response.status_code, 200)
        kv = KeyValue.objects.get(key='new')
        self.assertEqual(kv.value, "{'mykey': 'Value 2'}")
        response = self.client.delete('/kv/api/kv/%d/' % kv.pk)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(KeyValue.objects.filter(key="new").exists())

        self.client.login(username='user2', password='password')
        response = self.client.delete('/kv/api/kv/%d/' % self.kv_2_grp2.pk)
        self.assertEqual(response.status_code, 404)
        data = {'key': 'foobar'}
        response = self.client.patch('/kv/api/kv/%d/' % self.kv_2_grp2.pk, data,
                                     format='json')
        self.assertEqual(response.status_code, 404)
