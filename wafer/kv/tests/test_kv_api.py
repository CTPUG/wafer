"""Tests for wafer.kv api views."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import Client, TestCase
from wafer.kv.models import KeyValue
import json


def get_group(group):
    return Group.objects.get(name=group)


def create_group(group):
    grp = Group(name=group)
    grp.save()
    return grp


def create_user(username, groups):
    create = get_user_model().objects.create_user
    user = create(
        username, '%s@example.com' % username, 'password')
    for the_group in groups:
        grp = get_group(the_group)
        user.groups.add(grp)
    user.save()
    return user


def create_kv_pair(name, value, group):
    group = get_group(group)
    kv = KeyValue(key=name, value=value, group=group)
    kv.save()
    return kv


class KeyValueViewSetTests(TestCase):

    def setUp(self):
        for grp in ['group_1', 'group_2', 'group_3', 'group_4']:
            create_group(grp)
        self.user1 = create_user("user1", ["group_1", "group_2"])
        self.user2 = create_user("user2", ["group_1"]),
        self.user3 = create_user("user3", ["group_4"]),
        self.user4 = create_user("user4", ["group_3"]),
        self.kv_1_grp1 = create_kv_pair("Val 1.1", '{"key": "Data"}', "group_1")
        self.kv_2_grp2 = create_kv_pair("Val 2.1", '{"key2": "False"}', "group_2")
        self.kv_2_grp1 = create_kv_pair("Val 1.2", '{"key3": "True"}', "group_1")
        self.kv_3_grp1 = create_kv_pair("Val 1.3", '{"key1": "Data"}', "group_1")
        self.kv_3_grp3 = create_kv_pair("Val 3.1", '{"key1": "Data"}', "group_3")
        self.duplicate_name = create_kv_pair("Val 1.1", '{"key1": "Data"}', "group_3")
        self.client = Client()

    def test_unauthorized_users(self):
        response = self.client.get('/kv/api/kv/')
        self.assertEqual(response.data['count'], 0)
        response = self.client.get('/talks/api/kv/%d/' % self.kv_1_grp1.pk)
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
