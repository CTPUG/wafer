from django.contrib.auth import get_user_model

from rest_framework import serializers
from reversion import revisions

from wafer.talks.models import Talk, TalkUrl, ReviewAspect, Score, Review


class TalkUrlSerializer(serializers.ModelSerializer):

    talk = serializers.PrimaryKeyRelatedField(
        queryset=Talk.objects.all(), write_only=True)

    class Meta:
        model = TalkUrl
        fields = ('id', 'description', 'url', 'talk', 'public')
        read_only_fields = ('id',)


class PublicTalkUrlListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.exclude(public=False)
        return super().to_representation(data)


class PublicTalkUrlSerializer(TalkUrlSerializer):
    class Meta(TalkUrlSerializer.Meta):
        list_serializer_class = PublicTalkUrlListSerializer


class MarkdownSerializer(serializers.CharField):
    def get_attribute(self, instance):
        value = super().get_attribute(instance)
        return value.raw


class TalkSerializer(serializers.ModelSerializer):

    authors = serializers.PrimaryKeyRelatedField(
        many=True, allow_null=True,
        queryset=get_user_model().objects.all())

    abstract = MarkdownSerializer()

    urls = PublicTalkUrlSerializer(many=True, read_only=True)

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
        return super().create(validated_data)

    @revisions.create_revision()
    def update(self, talk, validated_data):
        revisions.set_comment("Changed via REST api")
        return super().update(talk, validated_data)


class ReviewAspectSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewAspect
        fields = ('name',)


class ReviewScoreSerializer(serializers.ModelSerializer):

    aspect = ReviewAspectSerializer()

    class Meta:
        model = Score
        fields = ('aspect', 'value')


class ReviewSerializer(serializers.ModelSerializer):

    scores = ReviewScoreSerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'talk', 'reviewer', 'notes', 'scores', 'avg_score')
