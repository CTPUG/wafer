"""Tests for scheduling provisionally accepted talks"""

import datetime as D

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from wafer.schedule.admin import (
    ScheduleItemAdminForm, validate_items_invalid_talk)
from wafer.schedule.models import (
    ScheduleBlock, ScheduleItem, Slot, Venue, schedulable_talk_statuses)
from wafer.talks.models import ACCEPTED, CANCELLED, PROVISIONAL, SUBMITTED
from wafer.talks.tests.fixtures import create_talk
from wafer.tests.utils import create_user


class ProvisionalTalksTests(TestCase):

    def setUp(self):
        self.accepted = create_talk('Accepted', ACCEPTED, username='a')
        self.provisional = create_talk('Provisional', PROVISIONAL,
                                       username='p')
        self.submitted = create_talk('Submitted', SUBMITTED, username='s')

        block = ScheduleBlock.objects.create(
            start_time=D.datetime(2013, 9, 22, 9, 0, tzinfo=D.timezone.utc),
            end_time=D.datetime(2013, 9, 22, 19, 0, tzinfo=D.timezone.utc))
        self.venue = Venue.objects.create(name='Venue 1', order=1, notes='')
        self.venue.blocks.add(block)
        self.slot = Slot.objects.create(
            start_time=D.datetime(2013, 9, 22, 10, 0, tzinfo=D.timezone.utc),
            end_time=D.datetime(2013, 9, 22, 11, 0, tzinfo=D.timezone.utc))

    def schedule(self, talk):
        item = ScheduleItem.objects.create(venue=self.venue, talk=talk)
        item.slots.add(self.slot)
        return item

    def admin_form_talks(self):
        return set(ScheduleItemAdminForm().fields['talk'].queryset)

    def editor_talks(self):
        create_user('admin', superuser=True)
        client = Client()
        client.login(username='admin', password='admin_password')
        response = client.get(reverse('admin:schedule_editor'))
        self.assertEqual(response.status_code, 200)
        return set(response.context['talks_all'])

    def test_statuses(self):
        self.assertEqual(schedulable_talk_statuses(), [ACCEPTED, CANCELLED])
        with self.settings(WAFER_SCHEDULE_PROVISIONAL_TALKS=True):
            self.assertEqual(schedulable_talk_statuses(),
                             [ACCEPTED, CANCELLED, PROVISIONAL])

    def test_not_schedulable_by_default(self):
        self.assertEqual(self.admin_form_talks(), {self.accepted})
        self.assertEqual(self.editor_talks(), {self.accepted})
        item = self.schedule(self.provisional)
        self.assertEqual(validate_items_invalid_talk([item]), [item])

    @override_settings(WAFER_SCHEDULE_PROVISIONAL_TALKS=True)
    def test_schedulable_when_enabled(self):
        self.assertEqual(self.admin_form_talks(),
                         {self.accepted, self.provisional})
        self.assertEqual(self.editor_talks(),
                         {self.accepted, self.provisional})
        item = self.schedule(self.provisional)
        self.assertEqual(validate_items_invalid_talk([item]), [])

    @override_settings(WAFER_SCHEDULE_PROVISIONAL_TALKS=True)
    def test_other_statuses_still_not_schedulable(self):
        self.assertNotIn(self.submitted, self.admin_form_talks())
        item = self.schedule(self.submitted)
        self.assertEqual(validate_items_invalid_talk([item]), [item])
