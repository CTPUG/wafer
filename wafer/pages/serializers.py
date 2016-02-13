from django.contrib.auth import get_user_model

from rest_framework import serializers
from reversion import revisions

from wafer.pages.models import Page


class PageSerializer(serializers.ModelSerializer):

    people = serializers.PrimaryKeyRelatedField(
        many=True, allow_null=True,
        queryset=get_user_model().objects.all())

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
        page.include_in_menu = validated_data['include_in_menu']
        page.exclude_from_static = validated_data['exclude_from_static']
        page.people = validated_data.get('people')
        page.save()
        return page
