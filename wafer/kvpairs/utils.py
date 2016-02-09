# -*- coding: utf-8 -*-
# (c) 2015-16 martin f. krafft <madduck@debconf.org>
# Released under the terms of the same licence as Wafer.

# make convenience functions accessible from app namespace, please refer to
# the KeyValuePair model for call signatures and documentation
from models import KeyValuePair

set_keyvalue_for_instance = KeyValuePair.set_keyvalue_for_instance
has_keyvalue_for_instance = KeyValuePair.has_keyvalue_for_instance
get_keyvalue_for_instance = KeyValuePair.get_keyvalue_for_instance
del_keyvalue_for_instance = KeyValuePair.del_keyvalue_for_instance
