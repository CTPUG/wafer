from rest_framework import serializers

from wafer.sponsors.models import Sponsor, SponsorshipPackage


class SponsorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sponsor

    def create(self, validated_data):
        # TODO: Implement
        return super(SponsorSerializer, self).create(validated_data)


class PackageSerializer(serializers.ModelSerializer):

    class Meta:
        model = SponsorshipPackage

    def create(self, validated_data):
        # TODO: Implement
        return super(PackageSerializer, self).create(validated_data)
