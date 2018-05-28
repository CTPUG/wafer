from rest_framework import serializers
from reversion import revisions

from wafer.talks.models import Talk
from wafer.pages.models import Page
from wafer.schedule.models import ScheduleItem, Venue, Slot


class ScheduleItemSerializer(serializers.HyperlinkedModelSerializer):
    page = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=Page.objects.all())
    talk = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=Talk.objects.all())
    venue = serializers.PrimaryKeyRelatedField(
        allow_null=True, queryset=Venue.objects.all())
    slots = serializers.PrimaryKeyRelatedField(
        allow_null=True, many=True, queryset=Slot.objects.all())

    class Meta:
        model = ScheduleItem
        fields = ('id', 'talk', 'page', 'venue', 'slots')

    @revisions.create_revision()
    def create(self, validated_data):
        request = self.context['request']
        venue_id = validated_data['venue']
        slots = validated_data['slots']
        talk = validated_data.get('talk')
        page = validated_data.get('page')

        try:
            existing_schedule_item = ScheduleItem.objects.get(
                venue_id=venue_id, slots__in=slots)
        except ScheduleItem.DoesNotExist:
            revisions.set_user(request.user)
            revisions.set_comment("Created using Schedule Editor")
        else:
            existing_schedule_item.talk = talk
            existing_schedule_item.page = page
            existing_schedule_item.slots = slots
            # Clear any existing details that aren't editable by the
            # schedule edit view
            existing_schedule_item.details = ''
            existing_schedule_item.notes = ''
            existing_schedule_item.css_class = ''
            existing_schedule_item.expand = False
            existing_schedule_item.save()
            revisions.set_user(request.user)
            revisions.set_comment("Updated using Schedule Editor")
            return existing_schedule_item
        return super(ScheduleItemSerializer, self).create(validated_data)
