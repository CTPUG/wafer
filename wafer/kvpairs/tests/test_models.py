# -*- coding: utf-8 -*-
# (c) 2015-16 martin f. krafft <madduck@debconf.org>
# Released under the terms of the same licence as Wafer.
#
# You know what this file does

from django.test import TestCase#, Client
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
User = get_user_model()
from django.contrib.contenttypes.models import ContentType

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from wafer.kvpairs.models import Key, KeyValuePair, \
        SUPPORTED_MODEL_TYPES

# we need another model for testing, let's use talks:
from wafer.talks.models import Talk


class _KVPairsTestCase(TestCase):

    def __init__(self, *args, **kwargs):
        super(_KVPairsTestCase, self).__init__(*args, **kwargs)
        self._counters = {}

    def _get_next_id(self, model):
        nid = self._counters.setdefault(model, 0) + 1
        self._counters[model] = nid
        return nid

    def _make_name(self, model, postfix=None):
        ret = 'test%s%d' % (model.__name__, self._get_next_id(model))
        if postfix:
            ret = '_'.join((ret, str(postfix)))
        return ret

    def _make_test_instance(self, model, nameadd=None, **kwargs):
        NAMEFIELDMAP = { User : 'username',
                        Talk : 'title'
                    }
        name = self._make_name(model, nameadd)
        kwargs.update({ NAMEFIELDMAP.get(model, 'name') : name })
        return model.objects.get_or_create(**kwargs)[0]

    def _make_owner_and_group(self):
        return (self._make_test_instance(User),
                self._make_test_instance(Group))


class KeyModelTests(_KVPairsTestCase):
    '''Tests for waver.kvpairs.models.Key'''

    def _make_key_returning_new_owner_group(self, name, **kwargs):
        owner, group = self._make_owner_and_group()
        return Key(owner=owner, group=group, name=name, **kwargs), \
            owner, group

    def _make_key_with_new_owner_group(self, name, **kwargs):
        return self._make_key_returning_new_owner_group(name, **kwargs)[0]

    def _make_key_for_model(self, name, model, **kwargs):
        return self._make_key_with_new_owner_group(name, model_class=model,
                **kwargs)

    def _make_key_for_ct_strings(self, name, app_label, model, **kwargs):
        return self._make_key_with_new_owner_group(name,
                app_label=app_label, model=model, **kwargs)

    def _make_key_for_ct_object(self, name, model_ct, **kwargs):
        return self._make_key_with_new_owner_group(name, model_ct=model_ct,
                **kwargs)

    def test_key_creation_owner_group(self):
        '''make sure creation works wrt owner/group'''
        k, u, g = self._make_key_returning_new_owner_group("testkey", model_class=User)
        self.assertEqual(k.owner, u)
        self.assertEqual(k.group, g)

    def test_key_creation_model(self):
        '''test creation from a model class'''
        name = "key from user model"
        k = self._make_key_for_model(name, User)
        ct = ContentType.objects.get_for_model(User)
        self.assertEqual(k.model_ct, ct)
        self.assertEqual(k.name, name)

    def test_key_creation_ct_object(self):
        '''test creation from a ContentType instance'''
        name = "key from user content_type"
        ct = ContentType.objects.get_for_model(User)
        k = self._make_key_for_ct_object(name, ct)
        self.assertEqual(k.model_ct, ct)
        self.assertEqual(k.name, name)

    def test_key_creation_ct_strings(self):
        '''test creation from ContentType strings'''
        name = "key from user content_type"
        ct = ContentType.objects.get_for_model(User)
        k = self._make_key_for_ct_strings(name, ct.app_label, ct.model)
        self.assertEqual(k.model_ct, ct)
        self.assertEqual(k.name, name)

    def test_unsupported_model_creation(self):
        '''test failure on creation of key for unsupported model'''
        testmodel = 'auth.permission'
        self.assertNotIn(testmodel, SUPPORTED_MODEL_TYPES)
        k = self._make_key_for_ct_strings("test",
                **dict(zip(('app_label', 'model'), testmodel.split('.'))))
        with self.assertRaises(ValidationError):
            k.full_clean()

    def test_keyname_cannot_be_null(self):
        '''test failure when null keyname is given'''
        k = self._make_key_for_model(None, User)
        with self.assertRaises(ValidationError):
            k.full_clean()

    def test_keyname_cannot_be_empty(self):
        '''test failure when empty keyname is given'''
        k = self._make_key_for_model('', User)
        with self.assertRaises(ValidationError):
            k.full_clean()

    def test_saving(self):
        '''test saving keys to database'''
        k = self._make_key_for_model("test", User)
        k.save()

    def test_repr(self):
        '''just verify the representation of the Key to'''
        k = self._make_key_for_model("test", User)
        # don't verify output, just that it works
        '%r' % k

    def test_keyname_must_be_unique_for_model(self):
        '''test unique constraints across (name, model)'''
        name = 'test'
        k1 = self._make_key_for_model(name, User)
        k1.save()
        k2 = self._make_key_for_model(name, User)
        with self.assertRaises(IntegrityError):
            k2.save()

    def test_keyname_needs_not_be_unique_across_models(self):
        '''ensure keynames are namespaced on models'''
        name = 'test'
        k1 = self._make_key_for_model(name, User)
        k1.save()
        k2 = self._make_key_for_model(name, Talk)
        k2.save()

    def test_getting_model_name(self):
        '''ensure we get a properly formatted name back'''
        ct = ContentType.objects.get_for_model(User)
        k = self._make_key_for_ct_object("foo", ct)
        self.assertEqual(k.get_model_name(), '%s.%s' % (ct.app_label,
            ct.model))

    def test_db_retrieval(self):
        '''test saving and retrieving data via the database'''
        name="via_db"
        model_ct=ContentType.objects.get_for_model(User)
        k = self._make_key_for_ct_object(name, model_ct)
        k.save()

        k2 = Key.objects.get(name=name, model_ct=model_ct)


class KeyValuePairModelTests(_KVPairsTestCase):
    '''Tests for waver.kvpairs.models.KeyValuePair'''

    def setUp(self):
        '''Set up keys used in the tests'''
        owner, group = self._make_owner_and_group()
        self.ukey = Key.objects.create(name="snores", model_class=User,
                owner=owner, group=group)
        self.tkey = Key.objects.create(name="video", model_class=Talk,
                owner=owner, group=group)

    def test_construction(self):
        '''Test construction of the key-value pair'''
        u = self._make_test_instance(User)
        value = 'yes'
        p = KeyValuePair(key=self.ukey, ref_id=u.pk, value=value)
        self.assertEqual(p.ref_id, u.pk)
        self.assertEqual(p.key, self.ukey)
        self.assertEqual(p.value, value)

    def test_saving(self):
        '''Test saving to database'''
        u = self._make_test_instance(User)
        p = KeyValuePair(key=self.ukey, ref_id=u.pk, value="yes")
        p.save()

    def test_repr(self):
        '''just verify the representation of the KeyValuePair to stdout'''
        u = self._make_test_instance(User)
        p = KeyValuePair(key=self.ukey, ref_id=u.pk, value="yes")
        # don't verify output, just that it works
        '%r' % p

    def test_only_one_value_per_key_object_combination(self):
        '''Ensure uniqueness of (key, ref_id)'''
        u = self._make_test_instance(User)
        p1 = KeyValuePair(key=self.ukey, ref_id=u.pk, value="yes")
        p1.save()
        p2 = KeyValuePair(key=self.ukey, ref_id=u.pk, value="no")
        with self.assertRaises(IntegrityError):
            p2.save()

    def test_value_retrieval(self):
        '''Test retrieving the value stored'''
        u = self._make_test_instance(User)
        value='yes'
        p = KeyValuePair(key=self.ukey, ref_id=u.pk, value=value)
        p.save()

        pr = KeyValuePair.objects.get(key=self.ukey, ref_id=u.pk)
        self.assertEqual(pr.ref_id, u.pk)
        self.assertEqual(pr.value, value)

    def test_value_retrieval_multiple(self):
        '''Test retrieving the value stored'''
        u1 = self._make_test_instance(User)
        u2 = self._make_test_instance(User)
        v1, v2 = 'one', 'two'
        p1 = KeyValuePair(key=self.ukey, ref_id=u1.pk, value=v1)
        p1.save()
        p2 = KeyValuePair(key=self.ukey, ref_id=u2.pk, value=v2)
        p2.save()

        for u,v in ((u1,v1),(u2,v2)):
            pr = KeyValuePair.objects.get(key=self.ukey, ref_id=u.pk)
            self.assertEqual(pr.ref_id, u.pk)
            self.assertEqual(pr.value, v)

    def test_value_cannot_be_null(self):
        '''test failure when null value is given'''
        u = self._make_test_instance(User)
        p = KeyValuePair(key=self.ukey, ref_id=u.pk, value=None)
        with self.assertRaises(ValidationError):
            p.full_clean()

    def test_value_cannot_be_empty(self):
        '''test failure when empty value is given'''
        u = self._make_test_instance(User)
        p = KeyValuePair(key=self.ukey, ref_id=u.pk, value='')
        with self.assertRaises(ValidationError):
            p.full_clean()

    def test_setting_with_key_creation(self):
        '''test implicit key creation'''
        u = self._make_test_instance(User)
        o = self._make_test_instance(User)
        k = 'room'
        v = 'A123'
        p = KeyValuePair.set_keyvalue_for_instance(u, k, v, owner=o,
                create_key=True)
        self.assertEqual(p.ref_id, u.pk)
        self.assertEqual(p.value, v)
        k2 = Key.objects.get(name=k)
        self.assertEqual(k2.model_ct,
                ContentType.objects.get_for_model(User))
        self.assertEqual(k2.owner, o)

    def test_failure_setting_with_key_creation_without_owner(self):
        '''test failure when owner is missing for implicit key creation'''
        u = self._make_test_instance(User)
        k = 'elvis %s' % hash(self)
        v = k[1]+k[3]+k[2]+k[0]+k[4]
        with self.assertRaises(ValueError):
            p = KeyValuePair.set_keyvalue_for_instance(u, k, v,
                    create_key=True)

    def test_failure_setting_nonexistent_key(self):
        '''test failure when setting and the key does not exist'''
        u = self._make_test_instance(User)
        k = 'jfk %s' % hash(self)
        v = 'mia'
        with self.assertRaises(Key.DoesNotExist):
            p = KeyValuePair.set_keyvalue_for_instance(u, k, v)

    def test_getting_value(self):
        '''test obtaining the value for a keyname/instance tuple'''
        u = self._make_test_instance(User)
        value = 'foobar'
        p = KeyValuePair(key=self.ukey, ref_id=u.pk, value=value)
        p.save()
        self.assertEqual(value,
                KeyValuePair.get_keyvalue_for_instance(u, self.ukey.name))

    def test_getting_value_key_not_found(self):
        '''test failure obtaining value for a nonexistent key'''
        u = self._make_test_instance(User)
        nonexistent = 'nonexistent %s' % hash(self)
        with self.assertRaises(Key.DoesNotExist):
            KeyValuePair.get_keyvalue_for_instance(u, nonexistent)

    def test_getting_value_no_value(self):
        '''test failure obtaining nonexistent value'''
        u = self._make_test_instance(User)
        with self.assertRaises(KeyValuePair.DoesNotExist):
            KeyValuePair.get_keyvalue_for_instance(u, 'snores')

    def test_getting_value_check_nonexistent(self):
        '''test checking for nonexistent value'''
        u = self._make_test_instance(User)
        self.assertFalse(KeyValuePair.has_keyvalue_for_instance(u, 'snores'))

    def test_getting_value_check_exists(self):
        '''test checking for nonexistent value'''
        u = self._make_test_instance(User)
        KeyValuePair.set_keyvalue_for_instance(u, 'snores', 'no')
        self.assertTrue(KeyValuePair.has_keyvalue_for_instance(u, 'snores'))

    def test_deleting_values(self):
        '''test deletion of key-value pair instances'''
        u = self._make_test_instance(User)
        KeyValuePair.set_keyvalue_for_instance(u, 'snores', 'oh baby!')
        KeyValuePair.del_keyvalue_for_instance(u, 'snores')
        self.assertFalse(KeyValuePair.has_keyvalue_for_instance(u, 'snores'))
