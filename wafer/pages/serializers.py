from rest_framework import serializers
from reversion import revisions

from wafer.pages.models import Page


class PageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Page
        exclude = ('_content_rendered',)

    @revisions.create_revision()
    def create(self, validated_data):
        revisions.set_comment("Created via REST api")
        return super(PageSerializer, self).create(validated_data)

    @revisions.create_revision()
    def update(self, page, validated_data):
        revisions.set_comment("Changed via REST api")
        page.parent = validated_data['parent']
        page.content = validated_data['content']
        page.save()
        return page
