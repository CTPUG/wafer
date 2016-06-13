from django.contrib.auth import get_user_model

from rest_framework import serializers
from reversion import revisions

from wafer.talks.models import Talk
from wafer.kv.serializers import CustomKeyValueSerializer
from wafer.kv.utils import update_kv


class TalkSerializer(serializers.ModelSerializer):

    authors = serializers.PrimaryKeyRelatedField(
        many=True, allow_null=True,
        queryset=get_user_model().objects.all())

    kv = CustomKeyValueSerializer()

    class Meta:
        model = Talk
        # private_notes should possibly be accessible to
        # talk reviewers by the API, but certainly
        # not to the other users.
        # Similar considerations apply to notes, which should
        # not be generally accessible
        exclude = ('_abstract_rendered', 'private_notes', 'notes')


    @revisions.create_revision()
    def create(self, validated_data):
        revisions.set_comment("Created via REST api")
        return super(TalkSerializer, self).create(validated_data)

    @revisions.create_revision()
    def update(self, talk, validated_data):
        revisions.set_comment("Changed via REST api")
        if 'abstract' in validated_data:
            talk.abstract = validated_data['abstract']
        if 'title' in validated_data:
            talk.title = validated_data['title']
        if 'talk_type' in validated_data:
            talk.talk_type = validated_data['talk_type']
        if 'authors' in validated_data:
            talk.authors = validated_data['authors']
        if 'status' in validated_data:
            talk.status = validated_data['status']
        if 'kv' in validated_data:
            update_kv(talk.kv, validated_data['kv'], self.context)
        # These need more thought
        #talk.notes = validated_data['notes']
        #talk.private_notes = validated_data['private_notes']
        talk.save()
        return talk
