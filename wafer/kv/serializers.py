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
