from rest_framework import serializers
from reversion import revisions

from wafer.talks.models import Talk


class TalkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Talk
        exclude = ('_abstract_rendered', )


    @revisions.create_revision()
    def create(self, validated_data):
        revisions.set_comment("Created via REST api")
        return super(TalkSerializer, self).create(validated_data)

    @revisions.create_revision()
    def update(self, talk, validated_data):
        revisions.set_comment("Changed via REST api")
        talk.abstract = validated_data['abstract']
        talk.title = validated_data['title']
        talk.status = validated_data['status']
        talk.talk_type = validated_data['talk_type']
        talk.notes = validated_data['notes']
        talk.private_notes = validated_data['private_notes']
        talk.save()
        return talk
