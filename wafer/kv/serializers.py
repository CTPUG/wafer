from rest_framework import serializers
from wafer.kv.models import KeyValue


class KeyValueSerializer(serializers.ModelSerializer):

    class Meta:
        model = KeyValue

    # There doesn't seem to be a better way of handling the problem
    # of filtering the groups.
    # See the DRF meta-issue https://github.com/tomchristie/django-rest-framework/issues/1985
    # and various related subdisscussions, such as https://github.com/tomchristie/django-rest-framework/issues/2292
    def __init__(self, *args, **kwargs):
        # XXX: Breaks introspection tools which call serializers
        # without a request
        user = kwargs['context']['request'].user

        if not user.is_superuser:
            # Limit to groups shown to those we're a member of
            groups = self.fields['group']
            groups.queryset = user.groups

        super(KeyValueSerializer, self).__init__(*args, **kwargs)
