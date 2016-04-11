from rest_framework import serializers
from wafer.kv.models import KeyValue


class KeyValueSerializer(serializers.ModelSerializer):

    class Meta:
        model = KeyValue
