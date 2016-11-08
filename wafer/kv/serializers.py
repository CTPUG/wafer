from django.core.exceptions import PermissionDenied
from rest_framework import serializers
from wafer.kv.models import KeyValue


class KeyValueSerializer(serializers.ModelSerializer):

    class Meta:
        model = KeyValue
        fields = ('group', 'key', 'value')

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

        super(KeyValueSerializer, self).__init__(*args, **kwargs)
