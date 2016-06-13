from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import NoReverseMatch
from rest_framework import serializers
from wafer.kv.models import KeyValue


class MaybeHyperlinkField(serializers.HyperlinkedRelatedField):
    """Overrider HyperlinkRelatedFiled to return just the object name
       for when a model has not been hooked up to the api, so we don't
       need to add special cases everytime a new model grows KV support
       without growing a API view."""

    def get_url(self, obj, view_name, request, format):
        try:
            return super(MaybeHyperlinkField, self).get_url(obj, view_name, request, format)
        except NoReverseMatch:
            return super(MaybeHyperlinkField, self).get_name(obj)


class CustomKeyValueSerializer(serializers.HyperlinkedRelatedField):

    # Because of how Django rest framework handles the dance between
    # ManyRelatedField and RelatedField, we must override __new__
    # to have this always behave as if 'many=True' was set
    def __new__(cls, *args, **kwargs):
        if 'view_name' not in kwargs:
            # queryset here is just to statisfy older versions of
            # rest-framework which don't check for overridding get_queryset.
            return cls.many_init(*args, view_name='keyvalue-detail',
                                 queryset=KeyValue.objects.none(), **kwargs)
        return super(CustomKeyValueSerializer, cls).__new__(cls, *args,
                                                            **kwargs)

    def get_queryset(self):
        """Custom queryset to limit key-value pairs returned to the
           requesting user's group for choices"""
        request = self.context.get('request', None)
        if request and request.user.id is not None:
            grp_ids = [x.id for x in request.user.groups.all()]
            return KeyValue.objects.filter(group_id__in=grp_ids).all()
        return KeyValue.objects.none()

    def get_url(self, obj, view_name, request, format):
        # Because of how rest-framework creates the list for the existing values
        # without evaluating get_queryset, we redact the non-group elements here
        # This does leak information about the number of KeyValue pairs set by other
        # groups, but is simpler than removing the entries entirely.
        if request.user.id is not None:
            grp_ids = [x.id for x in request.user.groups.all()]
            if obj.group.id not in grp_ids:
                return u"hidden"
            else:
                # Construct the url as usual.
                return super(CustomKeyValueSerializer, self).get_url(
                    obj, view_name, request, format)
        else:
            return u"hidden"


class KeyValueSerializer(serializers.ModelSerializer):

    class Meta:
        model = KeyValue

    # There doesn't seem to be a better way of handling the problem
    # of filtering the groups.
    # See the DRF meta-issue https://github.com/tomchristie/django-rest-framework/issues/1985
    # and various related subdisscussions, such as https://github.com/tomchristie/django-rest-framework/issues/2292
    def __init__(self, *args, **kwargs):
        # Explicitly fail with a hopefully informative error message
        # if there is no request. This is for introspection tools which
        # call serializers without a request
        if 'request' not in kwargs['context']:
            raise PermissionDenied("No request information provided."
                                   "The KeyValue API isn't available without "
                                   "an authorized user")
        user = kwargs['context']['request'].user

        # Limit to groups shown to those we're a member of
        groups = self.fields['group']
        groups.queryset = user.groups

        # Add fields for the models we have ManyToMany relationships defined for
        for field in self.Meta.model._meta.get_fields():
            if field.name not in self.fields and field.many_to_many:
                # XXX: Is there a better way to get the correct view_name out of the url config?
                view_name = '%s-detail' % field.related_model._meta.model_name
                self.fields[field.name] = MaybeHyperlinkField(source=field.get_accessor_name(),
                                                              view_name=view_name, read_only=True,
                                                              many=True)

        super(KeyValueSerializer, self).__init__(*args, **kwargs)
