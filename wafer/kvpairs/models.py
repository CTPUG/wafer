# -*- coding: utf-8 -*-
# (c) 2015-16 martin f. krafft <madduck@debconf.org>
# Released under the terms of the same licence as Wafer.

from django.db import models
from django.db.models import signals
from django.core.exceptions import SuspiciousOperation, ValidationError
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import python_2_unicode_compatible

from django.conf import settings
KEYNAME_MAXLEN = settings.WAFER_KVPAIRS_KEYNAME_MAXLEN
VALUE_MAXLEN = settings.WAFER_KVPAIRS_VALUE_MAXLEN
AUTOCREATE_KEYS = settings.WAFER_KVPAIRS_AUTOCREATE_KEYS

from .fields import IndirectGenericForeignKey


# the list of models to which keys can be "attached", not sure why we limit
# it, but it feels right. This feeds the choices parameter of the Key.model_ct
# field, and can be disabled right here…
SUPPORTED_MODEL_TYPES = ('sites.site', 'auth.user', 'users.userprofile',
        'pages.page', 'schedule.venue', 'schedule.scheduleitem', 'talks.talk',
        'sponsors.sponsorshippackages', 'sponsors.sponsor',
        'tickets.tickettype', 'tickets.ticket')


@python_2_unicode_compatible
class Key(models.Model):
    """Definition of a specific key related to another model"""

    # Key ownership, which controls who can access/modify the values
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
            on_delete=models.PROTECT, # could be SET(get_sentinel_user)…
            verbose_name='Key owner')
    group = models.ForeignKey('auth.Group', null=True, # groups are not mandatory
            on_delete=models.SET_NULL,
            verbose_name='Key owner group')

    # The contenttypes framework already has all the models, let's link to
    # that:
    def _get_supported_models_as_q():
        label_model_pairs = [s.split('.') for s in SUPPORTED_MODEL_TYPES]
        if not label_model_pairs:
            return models.Q()

        acc = None
        for a,m in label_model_pairs:
            qpair = models.Q(app_label=a) & models.Q(model=m)
            acc = qpair if acc is None else acc | qpair
        return acc
    model_ct = models.ForeignKey('contenttypes.ContentType',
            on_delete=models.CASCADE, verbose_name='Referenced model type',
            limit_choices_to=_get_supported_models_as_q)

    # Finally, the name of the key/attribute
    name = models.CharField(max_length=KEYNAME_MAXLEN,
            verbose_name='Key name')

    class Meta:
        unique_together = (('model_ct', 'name'),)
        verbose_name = 'Key'

    def _check_model_is_supported(self, model_ct):
        """
        Check that we support/allow creating keys for the given model type,
        which cannot be done with choices on the ForeignKey as ContentTypes
        aren't ready at the stage of class definition yet.
        """
        if model_ct.model_class() not in SUPPORTED_MODEL_CLASSES:
            raise UnsupportedModelForKey('No support to create Keys '
                    'for model: %s' %
                        self._format_model_name(model_ct.app_label,
                            model_ct.model))
        return True

    def __init__(self, *args, **kwargs):
        """
        Initialise a Key() instance. This can be done in three ways, depending
        on which arguments are passed:

        - model_class: a class object, e.g. Talk
        - model_ct: a ContentType instance for a model
        - model, app_label: strings describing a ContentType
        """
        if 'model_class' in kwargs:
            self._init_from_model_class(*args, **kwargs)
        elif 'model' in kwargs and 'app_label' in kwargs:
            self._init_from_ct_app_label_and_model(*args, **kwargs)
        else:
            self._init_from_model_ct(*args, **kwargs)

    def _init_from_model_class(self, *args, **kwargs):
        ct = ContentType.objects.get_for_model(kwargs.pop('model_class'))
        self._init_from_model_ct(model_ct=ct, *args, **kwargs)

    def _init_from_ct_app_label_and_model(self, *args, **kwargs):
        ct = ContentType.objects.get(app_label=kwargs.pop('app_label'),
                model=kwargs.pop('model'))
        self._init_from_model_ct(model_ct=ct, *args, **kwargs)

    def _init_from_model_ct(self, *args, **kwargs):
        super(Key, self).__init__(*args, **kwargs)

    @classmethod
    def _format_model_name(cls, app_label, model):
        return '.'.join((app_label, model))

    @classmethod
    def _format_model_class(cls, model_class):
        ct = ContentType.objects.get_for_model(model_class)
        return _format_model_name(ct.app_label, ct.model)

    def get_model_class(self):
        '''Return the class object of the model to which this key relates'''
        return self.model_ct.model_class()

    def get_model_name(self):
        '''Return the name of the model to which this Key is attached'''
        return self._format_model_name(self.model_ct.app_label,
                self.model_ct.model)
    # For direct use of this attribute in forms:
    get_model_name.short_description = model_ct.verbose_name
    get_model_name.admin_order_field = 'model_ct'

    def get_fully_qualified_key_name(self, quoted=False):
        '''Return the name of the key properly namespaced'''
        name = self.name.join(("'",)*2) if quoted else self.name
        return '/'.join((self.get_model_name(), name))
    # For direct use of this attribute in forms:
    get_fully_qualified_key_name.short_description = name.verbose_name
    get_fully_qualified_key_name.admin_order_field = 'name'

    def is_compatible_instance(self, instance):
        '''Return whether a given instance is compatible with the associated model'''
        return isinstance(instance, self.get_model_class())

    def natural_key(self):
        '''Return the natural key of this Key (for serialization)'''
        return self.model_ct.natural_key() + (self.name,)

    def __str__(self):
        '''Return an informative text display string for this Key'''
        return u"[%s] %s" % (
                'id:%s'%self.id if self.id else 'unsaved',
                self.get_fully_qualified_key_name(quoted=True))


@python_2_unicode_compatible
class KeyValuePair(models.Model):
    """Mapping of referenced model instances to values"""

    # The key definition to use
    key = models.ForeignKey('Key', on_delete=models.PROTECT,
            verbose_name='Base key context')

    # The foreign key to the actual object we're referencing, e.g. the User to
    # which we are attributing a value
    ref_id = models.PositiveIntegerField(
            verbose_name='ID of referenced model instance')

    # The logic for the indirect generic foreign key happens in the
    # IndirectGenericForeignKey field, which we need to instantiate, but it
    # doesn't actually hold any data.
    ref_obj = IndirectGenericForeignKey(ct_field_path='key.model_ct',
            fk_field='ref_id')

    # finally the value to store
    value = models.CharField(max_length=VALUE_MAXLEN,
            verbose_name='Value for key associated with model instance')

    class Meta:
        unique_together = (('key', 'ref_id'),)
        verbose_name = 'Key-value pair'

    def __str__(self):
        '''Return an informative text display string for this KeyValuePair'''
        return u'[%s] %s(%s)/\'%s\'="%s"' % (
                'id:%s'%self.id if self.id else 'unsaved',
                self.key.get_model_name(), self.get_ref_instance(),
                self.key.name, self.value)

    def get_model_class(self):
        '''Returns the model class associated with the Key'''
        return self.key.get_model_class()

    def get_ref_instance(self):
        '''Returns the instance referenced by the KeyValuePair'''
        model_class = self.get_model_class()
        return model_class.objects.get(pk=self.ref_id)
    # For direct use of this attribute in forms:
    get_ref_instance.short_description = ref_id.verbose_name
    get_ref_instance.admin_order_field = 'ref_id'

    @classmethod
    def _get_or_create_key_for_instance(cls, instance, name,
            owner=None, group=None, create_key=False):
        ct = ContentType.objects.get_for_model(instance.__class__)
        try:
            return Key.objects.get(name=name, model_ct=ct)
        except Key.DoesNotExist:
            if create_key:
                return Key.objects.create(name=name, model_ct=ct,
                        owner=owner, group=group)
            else:
                raise

    @classmethod
    def set_keyvalue_for_instance(cls, instance, name, value,
            owner=None, group=None, create_key=AUTOCREATE_KEYS):
        """
        Sets the value for a key for a specific instance, creating the key
        if necessary, but only if create_key is True (can be set in
        settings.py). This is designed a shortcut but should be used with care
        to not create keys e.g. when things are misspelt, etc..
        """
        key = cls._get_or_create_key_for_instance(instance=instance,
                name=name, owner=owner, group=group, create_key=create_key)
        p = KeyValuePair.objects.get_or_create(key=key, ref_obj=instance)[0]
        p.value = value
        p.save()
        return p

    @classmethod
    def _get_kvpair_for_instance(cls, instance, name, owner=None, group=None):
        key = cls._get_or_create_key_for_instance(instance=instance, name=name,
                owner=owner, group=group, create_key=False)
        return KeyValuePair.objects.get(key=key, ref_obj=instance)

    @classmethod
    def get_keyvalue_for_instance(cls, instance, name, owner=None, group=None):
        '''Returns the value for a key for a specific instance'''
        p = cls._get_kvpair_for_instance(instance=instance, name=name,
                owner=owner, group=group)
        return p.value

    @classmethod
    def has_keyvalue_for_instance(cls, instance, name, owner=None, group=None):
        '''Returns True if a the specified key has a value'''
        try:
            p = cls._get_kvpair_for_instance(instance=instance, name=name,
                    owner=owner, group=group)
        except (KeyValuePair.DoesNotExist, Key.DoesNotExist):
            return False
        return True

    @classmethod
    def del_keyvalue_for_instance(cls, instance, name, owner=None, group=None):
        '''Delete a key-value pair for an instance'''
        p = cls._get_kvpair_for_instance(instance=instance, name=name,
                owner=owner, group=group)
        p.delete()
