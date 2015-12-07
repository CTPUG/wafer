# -*- coding: utf-8 -*-
# (c) 2015-16 martin f. krafft <madduck@debconf.org>
# Released under the terms of the same licence as Wafer.

from .models import KeyValuePair

from django.conf import settings
AUTOCREATE_KEYS = settings.WAFER_KVPAIRS_AUTOCREATE_KEYS

class KVPairsMixin(object):
    '''Add key-value store accessor functions to a class'''

    def set_keyvalue(self, name, value, owner=None, group=None,
            create_key=AUTOCREATE_KEYS):
        """
        Sets the value for a key, creating the key if necessary, but only if
        create_key is True (can be set in settings.py)
        """
        return KeyValuePair.set_keyvalue_for_instance(self, name=name,
                value=value, owner=owner, group=group, create_key=create_key)

    def get_keyvalue(self, name, owner=None, group=None,
            create_key=AUTOCREATE_KEYS):
        '''Returns the value for a key'''
        return KeyValuePair.get_keyvalue_for_instance(self, name=name,
                owner=owner, group=group, create_key=create_key)

    def has_keyvalue(self, name, owner=None, group=None):
        '''Returns True if a the specified key has a value'''
        return KeyValuePair.has_keyvalue_for_instance(self, name=name,
                owner=owner, group=group)

    def del_keyvalue(self, instance, name, owner=None, group=None):
        '''Delete a key-value pair'''
        KeyValuePair.del_keyvalue_for_instance(self, name=name, owner=owner,
                group=group)
