from django.contrib.auth import get_user_model

from rest_framework import serializers
from reversion import revisions

from wafer.tickets.models import Ticket, TicketType


class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = ("id", "name")
        read_only_fields = ("id",)

    @revisions.create_revision()
    def create(self, validated_data):
        revisions.set_comment("Created via REST api")
        return super().create(validated_data)

    @revisions.create_revision()
    def update(self, ticket_type, validated_data):
        revisions.set_comment("Changed via REST api")
        return super().update(ticket_type, validated_data)


class TicketSerializer(serializers.ModelSerializer):

    # required, but only for creation
    barcode = serializers.IntegerField(required=False)

    type = serializers.PrimaryKeyRelatedField(
        allow_null=False, queryset=TicketType.objects.all()
    )

    user = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=get_user_model().objects.all()
    )

    class Meta:
        model = Ticket
        fields = ("barcode", "email", "type", "user")

    @revisions.create_revision()
    def create(self, validated_data):
        revisions.set_comment("Created via REST api")
        if "barcode" not in validated_data:
            raise serializers.ValidationError(
                "barcode required during ticket creation")
        return super().create(validated_data)

    @revisions.create_revision()
    def update(self, ticket, validated_data):
        revisions.set_comment("Changed via REST api")
        if "barcode" in validated_data:
            raise serializers.ValidationError(
                "barcode forbidden during ticket update")
        return super().update(ticket, validated_data)
