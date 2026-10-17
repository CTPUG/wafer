import datetime as D

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from wafer.pages.models import Page
from wafer.schedule.models import ScheduleBlock, Venue, Slot, ScheduleItem
from wafer.talks.models import ACCEPTED
from wafer.talks.tests.fixtures import create_talk
from wafer.tests.utils import create_user


def make_block(day_start, day_end):
    """ Make a schedule block (day). """
    return ScheduleBlock.objects.create(
        start_time=day_start, end_time=day_end)


def make_slot(day, start, end):
    """ Make a slot inside a day (ScheduleBlock). """
    slot = Slot.objects.create(
        start_time=D.datetime(day.year, day.month, day.day,
                              start.hour, start.minute, 0,
                              tzinfo=D.timezone.utc),
        end_time=D.datetime(day.year, day.month, day.day,
                            end.hour, end.minute, 0,
                            tzinfo=D.timezone.utc))
    return slot


def make_venue(name='Venue 1'):
    """ Make a venue. """
    return Venue.objects.create(order=1, name=name)


def make_talk_item(talk, venue, slots):
    """ Make a schedule item for a talk. """
    item = ScheduleItem.objects.create(venue=venue, talk=talk)
    item.slots.add(*slots)
    return item


class ChecklistViewTests(TestCase):

    def setUp(self):
        timezone.activate('UTC')
        self.day = D.date(2013, 9, 22)
        self.block = make_block(
            D.datetime(2013, 9, 22, 7, 0, 0, tzinfo=D.timezone.utc),
            D.datetime(2013, 9, 22, 19, 0, 0, tzinfo=D.timezone.utc))
        self.venue = make_venue()

    def make_talk_and_item(self, start=D.time(10, 0), end=D.time(11, 0)):
        talk = create_talk('Test Talk %s' % start, ACCEPTED, 'test_user%s' % start)
        slot = make_slot(self.day, start, end)
        item = make_talk_item(talk, self.venue, [slot])
        return talk, slot, item

    def test_checklist_item_view_requires_admin(self):
        """The per-talk checklist is only viewable by admins"""
        _, _, item = self.make_talk_and_item()
        url = reverse('wafer_checklist_item', kwargs={'pk': item.pk})

        response = Client().get(url)
        self.assertEqual(response.status_code, 302)

        create_user('non_admin', superuser=False)
        client = Client()
        client.login(username='non_admin', password='non_admin_password')
        response = client.get(url)
        self.assertEqual(response.status_code, 403)

        client = Client()
        create_user('admin', superuser=True)
        client.login(username='admin', password='admin_password')
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_checklist_item_view_content(self):
        """The per-talk checklist contains the talk details and checklist"""
        talk, slot, item = self.make_talk_and_item()
        create_user('admin', superuser=True)
        client = Client()
        client.login(username='admin', password='admin_password')
        response = client.get(reverse('wafer_checklist_item',
                                      kwargs={'pk': item.pk}))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Test Talk 10:00:00', content)
        self.assertIn('test_user10:00:00', content)
        self.assertIn('Venue 1', content)
        self.assertIn('10:00', content)
        # The warning times: 15, 10, 5 minutes before the presumed end
        # (with the default 5 minute buffer, the talk is presumed to end
        # at 10:55), and the presumed end itself
        self.assertIn('10:40', content)
        self.assertIn('10:45', content)
        self.assertIn('10:50', content)
        self.assertIn('10:55', content)
        # The checklist headings
        self.assertIn('Preparation Checklist', content)
        self.assertIn('Talk checklist', content)
        self.assertIn('Post talk', content)

    @override_settings(WAFER_CHECKLIST_TALK_END_BUFFER_MINUTES=10)
    def test_checklist_item_view_custom_buffer(self):
        """The buffer setting shifts the presumed end time earlier"""
        talk, slot, item = self.make_talk_and_item(D.time(10, 0), D.time(11, 0))
        create_user('admin', superuser=True)
        client = Client()
        client.login(username='admin', password='admin_password')
        response = client.get(reverse('wafer_checklist_item',
                                      kwargs={'pk': item.pk}))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        # Presumed end is 10:50, with warnings at 10:35/10:40/10:45
        self.assertIn('10:35', content)
        self.assertIn('10:40', content)
        self.assertIn('10:45', content)
        self.assertIn('10:50', content)
        # The real end time must not appear as a warning time
        self.assertNotIn('10:55', content)

    @override_settings(WAFER_CHECKLIST_WARNING_OFFSETS_MINUTES=(20, 0))
    def test_checklist_item_view_custom_warning_offsets(self):
        """The warning offsets setting changes the warning times shown"""
        talk, slot, item = self.make_talk_and_item(D.time(10, 0), D.time(11, 0))
        create_user('admin', superuser=True)
        client = Client()
        client.login(username='admin', password='admin_password')
        response = client.get(reverse('wafer_checklist_item',
                                      kwargs={'pk': item.pk}))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        # Presumed end is 10:55 (default buffer), so warnings are 10:35 and 10:55
        self.assertIn('10:35', content)
        self.assertIn('10:55', content)
        # The default offsets must not appear
        self.assertNotIn('10:40', content)
        self.assertNotIn('10:45', content)
        self.assertNotIn('10:50', content)

    def test_checklist_item_view_non_talk_items(self):
        """Checklists are only available for scheduled talks"""
        page = Page.objects.create(name='test page', slug='testpage')
        item = ScheduleItem.objects.create(
            venue=self.venue, details='A page item', page_id=page.pk)
        create_user('admin', superuser=True)
        client = Client()
        client.login(username='admin', password='admin_password')
        response = client.get(reverse('wafer_checklist_item',
                                      kwargs={'pk': item.pk}))
        self.assertEqual(response.status_code, 404)

    def test_checklist_venue_view_requires_admin(self):
        """The venue checklist is only viewable by admins"""
        url = reverse('wafer_checklist_venue', kwargs={'pk': self.venue.pk})

        response = Client().get(url)
        self.assertEqual(response.status_code, 302)

        create_user('non_admin', superuser=False)
        client = Client()
        client.login(username='non_admin', password='non_admin_password')
        response = client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_checklist_venue_view_content(self):
        """The venue checklist contains all scheduled talks in the venue"""
        talk1, _, item1 = self.make_talk_and_item(D.time(10, 0), D.time(11, 0))
        talk2, _, item2 = self.make_talk_and_item(D.time(12, 0), D.time(13, 0))
        create_user('admin', superuser=True)
        client = Client()
        client.login(username='admin', password='admin_password')
        response = client.get(reverse('wafer_checklist_venue',
                                      kwargs={'pk': self.venue.pk}))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Test Talk 10:00:00', content)
        self.assertIn('Test Talk 12:00:00', content)
        self.assertIn(self.venue.name, content)
        # Talks are in slot order
        self.assertLess(content.index('Test Talk 10:00:00'),
                        content.index('Test Talk 12:00:00'))

    def test_checklist_venue_view_excludes_other_venues(self):
        """The venue checklist only includes talks for the given venue"""
        _, _, item = self.make_talk_and_item()
        other_venue = make_venue(name='Venue 2')
        other_talk = create_talk('Other Venue Talk', ACCEPTED, 'other_user')
        other_slot = make_slot(self.day, D.time(14, 0), D.time(15, 0))
        make_talk_item(other_talk, other_venue, [other_slot])
        create_user('admin', superuser=True)
        client = Client()
        client.login(username='admin', password='admin_password')
        response = client.get(reverse('wafer_checklist_venue',
                                      kwargs={'pk': self.venue.pk}))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Test Talk 10:00:00', content)
        self.assertNotIn('Other Venue Talk', content)

    def test_checklist_venue_view_excludes_pages(self):
        """The venue checklist only includes talks, not pages or breaks"""
        _, _, item = self.make_talk_and_item()
        page = Page.objects.create(name='test page', slug='testpage')
        page_item = ScheduleItem.objects.create(
            venue=self.venue, details='A page item', page_id=page.pk)
        page_item.slots.add(make_slot(self.day, D.time(13, 0), D.time(14, 0)))
        create_user('admin', superuser=True)
        client = Client()
        client.login(username='admin', password='admin_password')
        response = client.get(reverse('wafer_checklist_venue',
                                      kwargs={'pk': self.venue.pk}))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Test Talk 10:00:00', content)
        self.assertNotIn('A page item', content)

    def test_checklist_venue_view_multiple_days(self):
        """Talks on different days are grouped on separate pages"""
        other_day = D.date(2013, 9, 23)
        make_block(
            D.datetime(2013, 9, 23, 7, 0, 0, tzinfo=D.timezone.utc),
            D.datetime(2013, 9, 23, 19, 0, 0, tzinfo=D.timezone.utc))
        talk1, _, item1 = self.make_talk_and_item(D.time(10, 0), D.time(11, 0))
        talk2 = create_talk('Day 2 Talk', ACCEPTED, 'day2_user')
        slot2 = make_slot(other_day, D.time(10, 0), D.time(11, 0))
        make_talk_item(talk2, self.venue, [slot2])
        create_user('admin', superuser=True)
        client = Client()
        client.login(username='admin', password='admin_password')
        response = client.get(reverse('wafer_checklist_venue',
                                      kwargs={'pk': self.venue.pk}))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Test Talk 10:00:00', content)
        self.assertIn('Day 2 Talk', content)
        self.assertEqual(content.count('class="checklist-day"'), 2)

    def test_checklist_item_view_no_slots(self):
        """Talks with no slots show a warning in the checklist"""
        talk = create_talk('Unscheduled Talk', ACCEPTED, 'unscheduled_user')
        item = ScheduleItem.objects.create(venue=self.venue, talk=talk)
        create_user('admin', superuser=True)
        client = Client()
        client.login(username='admin', password='admin_password')
        response = client.get(reverse('wafer_checklist_item',
                                      kwargs={'pk': item.pk}))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Unscheduled Talk', content)
        self.assertIn('WARNING', content)
