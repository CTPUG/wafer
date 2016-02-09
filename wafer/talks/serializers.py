from rest_framework import serializers

from wafer.talks.models import Talk


class TalkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Talk

    def create(self, validated_data):
        # TODO: Implement
        return super(TalkSerializer, self).create(validated_data)
