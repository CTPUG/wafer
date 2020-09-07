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
        return super(TicketTypeSerializer, self).create(validated_data)

    @revisions.create_revision()
    def update(self, ticket_type, validated_data):
        revisions.set_comment("Changed via REST api")
        return super(TicketTypeSerializer, self).update(
            ticket_type, validated_data,
        )


class TicketSerializer(serializers.ModelSerializer):

    type = TicketTypeSerializer()

    user = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=get_user_model().objects.all()
    )

    class Meta:
        model = Ticket
        fields = ("id", "barcode", "email", "talk")
        read_only_fields = ("id",)

    @revisions.create_revision()
    def create(self, validated_data):
        revisions.set_comment("Created via REST api")
        return super(TicketSerializer, self).create(validated_data)

    @revisions.create_revision()
    def update(self, ticket, validated_data):
        revisions.set_comment("Changed via REST api")
        return super(TicketSerializer, self).update(ticket, validated_data)
