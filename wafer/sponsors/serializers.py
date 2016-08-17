from rest_framework import serializers
from reversion import revisions

from wafer.sponsors.models import Sponsor, SponsorshipPackage


class SponsorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sponsor
        exclude = ('_description_rendered', )

    @revisions.create_revision()
    def create(self, validated_data):
        revisions.set_comment("Created via REST api")
        return super(SponsorSerializer, self).create(validated_data)

    @revisions.create_revision()
    def update(self, sponsor, validated_data):
        revisions.set_comment("Changed via REST api")
        sponsor.name = validated_data['name']
        sponsor.description = validated_data['description']
        sponsor.save()
        return sponsor


class PackageSerializer(serializers.ModelSerializer):

    class Meta:
        model = SponsorshipPackage
        exclude = ('_description_rendered', )

    @revisions.create_revision()
    def create(self, validated_data):
        revisions.set_comment("Created via REST api")
        return super(PackageSerializer, self).create(validated_data)

    @revisions.create_revision()
    def update(self, package, validated_data):
        revisions.set_comment("Changed via REST api")
        package.name = validated_data['name']
        package.number_available = validated_data['number_available']
        package.description = validated_data['description']
        package.short_description = validated_data['short_description']
        package.price = validated_data['price']
        package.save()
        return package
