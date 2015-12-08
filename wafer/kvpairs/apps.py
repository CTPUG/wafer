# -*- coding: utf-8 -*-
# (c) 2015-16 martin f. krafft <madduck@debconf.org>
# Released under the terms of the same licence as Wafer.

from django.apps import AppConfig


class KVPairsConfig(AppConfig):
    name = 'wafer.kvpairs'
    label = 'kvpairs'
    verbose_name = 'Key-value storage'
