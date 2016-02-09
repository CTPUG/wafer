# -*- coding: utf-8 -*-
# (c) 2015-16 martin f. krafft <madduck@debconf.org>
# Released under the terms of the same licence as Wafer.

from django.core.exceptions import SuspiciousOperation, ValidationError
try:
    from django.core.exceptions import FieldDoesNotExist
except ImportError:
    # The exception class was not in core but in db.models in Django 1.7
    from django.db.models import FieldDoesNotExist

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.encoding import python_2_unicode_compatible


class IndirectGenericForeignKey(GenericForeignKey):
    """
    A pseudo-field implementing `contenttypes.GenericForeignKey` functionality
    in a way that the content type field can be stored in a different model
    referenced by the field's parent model using a `ForeignKey`.

    Similar to `contenttypes.GenericForeignKey`, this happens through two
    auxiliary fields holding the actual data. The first (referenced by
    `ct_field_path` is a ForeignKey to a `contenttypes.ContentType` instance,
    while the second (`fk_field`) is the local field holding the primary key
    (ID) of the instance that's being referenced. A model instance referencing
    e.g. `auth.user` with ID 42 would have its `ct_field_path` point to
    the `contenttypes.ContentType` instance for `auth.user`, and would store
    42 in its `fk_field`.

    This differs from `contenttypes.GenericForeignKey` in that the `ct_field`
    needs not be local to the model, but can be in a related model. For
    instance, `ct_field_path=foo.bar.model_ct` means that the content type is
    to be found in the `model_ct` field of the model referenced by the
    ForeignKey chain `foo.bar`, that is in the model referenced in ForeignKey
    field `bar` of the mode referenced in ForeignKey field `foo` of the model
    defining the field::

        class MyModel(models.Model):
            obj = IndirectGenericForeignKey(ct_field_path='foo.bar.model_ct', …)
            ref = fields.PositiveIntegerField()
            foo = fields.ForeignKey('Foo')

        class Foo(models.Model):
            bar = fields.ForeignKey('Bar')

        class Bar(models.Model):
            model_ct = ForeignKey('contenttypes.ContentType', …)

    As a consequence of this indirection, the `obj` field may only be assigned
    with a compatible instance, i.e. it is not possible to change the indirect
    `contenttypes.ContentType` reference through mere assignment, as one can
    do with `contenttypes.GenericForeignKey`.

    In all other aspects, `IndirectGenericForeignKey` should behave just like
    `contenttypes.GenericForeignKey`. If `ct_model_path` is just a fieldname,
    then the field should in fact behave exactly like
    `contenttypes.GenericForeignKey`.
    """

    def __init__(self, ct_field_path='content_type', fk_field='object_id',
            for_concrete_model=True):
        '''Initialise an IndirectGenericForeignKey instance'''
        parts = ct_field_path.split('.')
        if len(parts) > 1:
            self.ct_model_path = parts[:-1]
        else:
            self.ct_model_path = None  # the class itself is the referenced model
        super(IndirectGenericForeignKey, self).__init__(ct_field=parts[-1],
                fk_field=fk_field, for_concrete_model=for_concrete_model)

    def _resolve_model_path(self, path, start=None):
        model = start if start else self.model
        for p in path[::-1]:
            try:
                model = model._meta.get_field(p).related_model
            except AttributeError:
                model = model._meta.get_field(p).rel.to
        return model

    def _check_content_type_field(self):
        if self.ct_model_path:
            errors = []
            try:
                model = self._resolve_model_path(self.ct_model_path)
                field = model._meta.get_field(self.ct_field)
            except FieldDoesNotExist:
                errors = [
                    checks.Error(
                        "The IndirectGenericForeignKey content type references the non-existent field '%s.%s'." % (
                            '.'.join(self.ct_model_path) , self.ct_field
                        ),
                        hint=None,
                        obj=self,
                        id='contenttypes.E002',
                    )
                ]
        else:
            errors = super(IndirectGenericForeignKey, self)._check_content_type_field()

        return errors

    def _resolve_instance_path(self, path, start=None):
        ref = start if start else self._meta.model
        for p in path[::-1]:
            ref = getattr(ref, p)
        return ref

    def instance_pre_init(self, signal, sender, args, kwargs, **_kwargs):
        """
        The instance pre-initialisation hook, responsible for setting up field
        access. This essentially happens in two ways:

        First, the indirectly referenced content type (which is immutable) is
        pulled into the instance, for easier access.

        Second, the Django-specific data massaging functions used to proxy
        between the database and the Python types are essentially copied from
        the field holding the primary key of the instance that's being
        referenced. The only function that cannot be simply copied,
        `get_prep_lookup` is defined explicitly.

        All this cannot happen in the model definition or at setup time, since
        we need access to the data initialising an instance to obtain the
        indirect reference to `contenttypes.ContentType`, which is a run-time
        datum. Hence this is implemented as a `pre_init` hook and must
        manipulate `kwargs` accordingly.
        """
        super(IndirectGenericForeignKey, self).instance_pre_init(signal, sender, args, kwargs, **_kwargs)

        if kwargs.get(self.ct_field, False):
            self.indirect_ct_instance = self._resolve_instance_path(self.ct_model_path[:-1],
                    kwargs.get(self.ct_model_path[-1]))
            self.indirect_ct_field = self.indirect_ct_instance._meta.model._meta.get_field(self.ct_field)
            self.indirect_ct = getattr(self.indirect_ct_instance, self.ct_field)
            ct = kwargs.pop(self.ct_field)
            assert self.indirect_ct == ct, \
                    "init would assign value of type '%s' " \
                    "where type '%s' is expected" % (ct, self.indirect_ct)
            self.related_model = self.indirect_ct.model_class()

        fkfield = self.model._meta.get_field(self.fk_field)
        # proxy access for the following set of functions to the `fk_field`,
        # using a proxy accessor method. We could just use setattr here, but
        # using a method makes for easier debugging.
        for fn in ('get_col',           'get_lookup', 'get_prep_value',
                   'get_internal_type', 'db_type',    'get_db_prep_lookup'):
            self._install_fkfield_proxy_method(fkfield, fn)

    def _install_fkfield_proxy_method(self, fkfield, fn):
        try:
            method = getattr(fkfield, fn)
        except AttributeError:
            if fn == 'get_col':
                # Django 1.7 does not have get_col
                from django.db.models.datastructures import Col
                def method(self, alias, source):
                    return Col(alias, self, source)
            else:
                raise

        def fkfield_method_proxy(*args, **kwargs):
            return method(*args, **kwargs)
        fkfield_method_proxy.__name__ = method.__name__
        fkfield_method_proxy.__doc__ = method.__doc__
        setattr(self, fn, fkfield_method_proxy)

    def get_prep_lookup(self, *args, **kwargs):
        """
        Translate an object used during lookups using its primary key field.

        This is a necessity to allow manager functions to be naturally used
        with instances of the referenced content type, e.g.

          KeyValuePair.objects.get(ref_obj=SomeTalk, …)

        Without this translation, we'd have to remember to pass in SomeTalk's
        primary key instead.
        """
        args = (args[0], args[1]._get_pk_val())
        return self.model._meta.get_field(self.fk_field).get_prep_lookup(*args, **kwargs)

    def __get__(self, instance, instance_type=None):
        """
        Get the instance referenced by an `IndirectGenericForeignKey`
        instance, e.g. return the `Talk` instance referenced by
        a `KeyValuePair` referencing a `Key` applicable to the `Talk` model
        (instead of just returning the primary key and leaving it up to the
        user to obtain the related instance using the indirectly accessible
        content type.

        This is modeled very closely on
        `contenttypes.GenericForeignKey.__get__` with the only notable
        exception being that we access the right `ct_id` field (since
        `contenttypes.GenericForeignKey` hard-codes the requirement for this
        field to be local to the same model). Unfortunately, there seems no
        other way to modify the behaviour than to override the entire
        function.
        """
        if instance is None: return self

        try:
            return getattr(instance, self.cache_attr)
        except AttributeError:
            rel_obj = None
            # The following line is the only one different from the code in
            # `contenttypes.GenericForeignKey.__get__`.
            ct_id = getattr(self.indirect_ct_instance,
                    self.indirect_ct_field.get_attname())
            if ct_id:
                ct = self.get_content_type(id=ct_id, using=instance._state.db)
                try:
                    rel_obj = ct.get_object_for_this_type(pk=getattr(instance, self.fk_field))
                except ObjectDoesNotExist:
                    pass
            setattr(instance, self.cache_attr, rel_obj)
            return rel_obj

    def __set__(self, instance, value):
        """
        Assign an instance to the field. This is modeled very closely on
        `contenttypes.GenericForeignKey.__get__` with the only notable
        exception being that the content type is considered immutable and an
        exception will be thrown if an instance of incompatible content type
        is being assigned.
        """
        ct = None
        fk = None
        if value is not None:
            ct = self.get_content_type(obj=value)
            if self.get_content_type(obj=value) != self.indirect_ct:
                raise TypeError("Cannot assign value '%s' of type '%s' "
                                "when type '%s' is expected"
                                (value, ct, self.indirect_ct))
            fk = value._get_pk_val()

        setattr(instance, self.fk_field, fk)
        setattr(instance, self.cache_attr, value)

    def __repr__(self):
        '''Displays the module, class and name of the field'''
        path = '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
        name = getattr(self, 'name', None)
        if name is not None:
            return '<%s: %s>' % (path, name)
        return '<%s>' % path
