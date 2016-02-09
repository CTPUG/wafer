from rest_framework import serializers

from wafer.pages.models import Page


class PageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Page

    def create(self, validated_data):
        # TODO: Implement
        return super(PageSerializer, self).create(validated_data)
