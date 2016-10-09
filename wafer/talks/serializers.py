from django.contrib.auth import get_user_model

from rest_framework import serializers
from reversion import revisions

from wafer.talks.models import Talk, TalkUrl


class TalkUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = TalkUrl
        fields = ('id', 'description', 'url')
        read_only_fields = ('id',)


class TalkSerializer(serializers.ModelSerializer):

    authors = serializers.PrimaryKeyRelatedField(
        many=True, allow_null=True,
        queryset=get_user_model().objects.all())

    abstract = serializers.CharField(source='abstract.raw')

    urls = TalkUrlSerializer(source='talkurl_set', many=True)

    class Meta:
        model = Talk
        # private_notes should possibly be accessible to
        # talk reviewers by the API, but certainly
        # not to the other users.
        # Similar considerations apply to notes, which should
        # not be generally accessible
        fields = (
            'talk_id', 'talk_type', 'title', 'abstract', 'status', 'authors',
            'corresponding_author', 'urls', 'kv')
        read_only_fields = (
            'talk_id', 'urls', 'kv')

    @revisions.create_revision()
    def create(self, validated_data):
        revisions.set_comment("Created via REST api")
        return super(TalkSerializer, self).create(validated_data)

    @revisions.create_revision()
    def update(self, talk, validated_data):
        revisions.set_comment("Changed via REST api")
        talk.abstract = validated_data['abstract']
        talk.title = validated_data['title']
        talk.talk_type = validated_data['talk_type']
        talk.authors = validated_data['authors']
        talk.status = validated_data['status']
        # These need more thought
        # talk.notes = validated_data['notes']
        # talk.private_notes = validated_data['private_notes']
        talk.save()
        return talk
