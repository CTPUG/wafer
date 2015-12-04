# -*- coding: utf-8 -*-
# (c) 2015-16 martin f. krafft <madduck@debconf.org>
# Released under the terms of the same licence as Wafer.

from django.contrib import admin
from wafer.kvpairs.models import Key, KeyValuePair


@admin.register(Key)
class KeyAdmin(admin.ModelAdmin):
    fields = (('owner', 'group'), 'model_ct', 'name')
    list_display = ('get_fully_qualified_key_name', 'owner', 'group')
    search_fields = ('name',)


@admin.register(KeyValuePair)
class KeyValuePairAdmin(admin.ModelAdmin):
    fields = ('key', 'ref_id', 'value')
    list_display = ('key', 'get_ref_instance', 'value')
    search_fields = ('value',)
    list_editable = ('value',)
