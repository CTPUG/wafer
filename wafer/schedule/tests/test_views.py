import json
import datetime as D
import icalendar
from xml.etree import ElementTree

from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from wafer.talks.models import Talk, ACCEPTED
from wafer.pages.models import Page
from wafer.schedule.models import ScheduleBlock, Venue, Slot, ScheduleItem
from wafer.utils import QueryTracker


def make_pages(n):
    """ Make n pages. """
    pages = []
    for x in range(n):
        page = Page.objects.create(name="test page %s" % x,
                                   slug="test%s" % x)
        pages.append(page)
    return pages


def make_items(venues, pages, expand=()):
    """ Make items for pairs of venues and pages. """
    items = []
    for x, (venue, page) in enumerate(zip(venues, pages)):
        item = ScheduleItem.objects.create(venue=venue,
                                           details="Item %s" % x,
                                           page_id=page.pk,
                                           expand=x in expand)
        items.append(item)
    return items


def make_venue(order=1, name='Venue 1'):
    """ Make a venue. """
    venue = Venue.objects.create(order=1, name='Venue 1')
    return venue


def make_slot():
    """ Make a slot. """
    day = ScheduleBlock.objects.create(
            start_time=D.datetime(2013, 9, 22, 7, 0, 0,
                                  tzinfo=timezone.utc),
            end_time=D.datetime(2013, 9, 22, 19, 0, 0,
                                tzinfo=timezone.utc),
            )
    start = D.datetime(2013, 9, 22, 10, 0, 0,
                       tzinfo=timezone.utc)
    end = D.datetime(2013, 9, 22, 15, 0, 0, tzinfo=timezone.utc)
    slot = Slot.objects.create(start_time=start, end_time=end)
    return slot


def create_client(username=None, superuser=False):
    client = Client()
    if username:
        email = '%s@example.com' % (username,)
        password = '%s_password' % (username,)
        if superuser:
            create = get_user_model().objects.create_superuser
        else:
            create = get_user_model().objects.create_user
        create(username, email, password)
        client.login(username=username, password=password)
    return client


class ScheduleViewTests(TestCase):

    def setUp(self):
        timezone.activate('UTC')

    def test_simple_table(self):
        """Create a simple, single day table with 3 slots and 2 venues and
           check we get the expected results"""

        # Schedule is
        #         Venue 1     Venue 2
        # 10-11   Item1       Item4
        # 11-12   Item2       Item5
        # 12-13   Item3       Item6
        day1 = ScheduleBlock.objects.create(
            start_time=D.datetime(2013, 9, 22, 7, 0, 0,
                                  tzinfo=timezone.utc),
            end_time=D.datetime(2013, 9, 22, 19, 0, 0,
                                tzinfo=timezone.utc),
            )

        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue1.blocks.add(day1)
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue2.blocks.add(day1)

        start1 = D.datetime(2013, 9, 22, 10, 0, 0,
                            tzinfo=timezone.utc)
        start2 = D.datetime(2013, 9, 22, 11, 0, 0,
                            tzinfo=timezone.utc)
        start3 = D.datetime(2013, 9, 22, 12, 0, 0,
                            tzinfo=timezone.utc)
        end = D.datetime(2013, 9, 22, 13, 0, 0,
                         tzinfo=timezone.utc)

        pages = make_pages(6)
        venues = [venue1, venue1, venue1, venue2, venue2, venue2]
        items = make_items(venues, pages)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2)
        slot2 = Slot.objects.create(previous_slot=slot1, end_time=start3)
        slot3 = Slot.objects.create(previous_slot=slot2, end_time=end)

        items[0].slots.add(slot1)
        items[3].slots.add(slot1)
        items[1].slots.add(slot2)
        items[4].slots.add(slot2)
        items[2].slots.add(slot3)
        items[5].slots.add(slot3)

        c = Client()
        with QueryTracker() as tracker:
            response = c.get('/schedule/')
            self.assertTrue(len(tracker.queries) < 60)

        [day1] = response.context['schedule_pages']

        assert len(day1.rows) == 3
        assert day1.venues == [venue1, venue2]
        assert day1.rows[0].slot.get_start_time() == start1
        assert day1.rows[0].slot.end_time == start2
        assert day1.rows[1].slot.get_start_time() == start2
        assert day1.rows[1].slot.end_time == start3
        assert day1.rows[2].slot.get_start_time() == start3
        assert day1.rows[2].slot.end_time == end

        assert len(day1.rows[0].items) == 2
        assert len(day1.rows[1].items) == 2
        assert len(day1.rows[2].items) == 2

        assert day1.rows[0].get_sorted_items()[0]['item'] == items[0]
        assert day1.rows[0].get_sorted_items()[0]['rowspan'] == 1
        assert day1.rows[0].get_sorted_items()[0]['colspan'] == 1

        assert day1.rows[0].get_sorted_items()[1]['item'] == items[3]
        assert day1.rows[0].get_sorted_items()[1]['rowspan'] == 1
        assert day1.rows[0].get_sorted_items()[1]['colspan'] == 1

        assert day1.rows[1].get_sorted_items()[0]['item'] == items[1]
        assert day1.rows[1].get_sorted_items()[0]['rowspan'] == 1
        assert day1.rows[1].get_sorted_items()[0]['colspan'] == 1

        assert day1.rows[2].get_sorted_items()[1]['item'] == items[5]
        assert day1.rows[2].get_sorted_items()[1]['rowspan'] == 1
        assert day1.rows[2].get_sorted_items()[1]['colspan'] == 1

    def test_ordering(self):
        """Ensure we handle oddly ordered creation of items correctly"""
        # Schedule is
        #         Venue 1     Venue 2
        # 10-11   Item3       Item6
        # 11-12   Item2       Item5
        # 12-13   Item1       Item4
        day1 = ScheduleBlock.objects.create(
            start_time=D.datetime(2013, 9, 22, 7, 0, 0,
                                  tzinfo=timezone.utc),
            end_time=D.datetime(2013, 9, 22, 19, 0, 0,
                                tzinfo=timezone.utc),
            )
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue1.blocks.add(day1)
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue2.blocks.add(day1)

        start1 = D.datetime(2013, 9, 22, 10, 0, 0, tzinfo=timezone.utc)
        start2 = D.datetime(2013, 9, 22, 11, 0, 0, tzinfo=timezone.utc)
        start3 = D.datetime(2013, 9, 22, 12, 0, 0, tzinfo=timezone.utc)
        end = D.datetime(2013, 9, 22, 13, 0, 0, tzinfo=timezone.utc)

        pages = make_pages(6)
        venues = [venue1, venue1, venue1, venue2, venue2, venue2]
        items = make_items(venues, pages)

        # Create the slots not in date order either

        slot1 = Slot.objects.create(start_time=start1, end_time=start2)
        slot3 = Slot.objects.create(previous_slot=slot1, end_time=end)
        slot2 = Slot.objects.create(previous_slot=slot1, end_time=start3)
        slot3.previous_slot = slot2
        slot3.save()

        items[0].slots.add(slot3)
        items[3].slots.add(slot3)
        items[1].slots.add(slot2)
        items[4].slots.add(slot2)
        items[2].slots.add(slot1)
        items[5].slots.add(slot1)

        c = Client()
        response = c.get('/schedule/')

        [day1] = response.context['schedule_pages']

        assert len(day1.rows) == 3
        assert day1.venues == [venue1, venue2]
        assert day1.rows[0].slot.get_start_time() == start1
        assert day1.rows[0].slot.end_time == start2
        assert day1.rows[1].slot.get_start_time() == start2
        assert day1.rows[1].slot.end_time == start3
        assert day1.rows[2].slot.get_start_time() == start3
        assert day1.rows[2].slot.end_time == end

        assert len(day1.rows[0].items) == 2
        assert len(day1.rows[1].items) == 2
        assert len(day1.rows[2].items) == 2

        assert day1.rows[0].get_sorted_items()[0]['item'] == items[2]
        assert day1.rows[0].get_sorted_items()[0]['rowspan'] == 1
        assert day1.rows[0].get_sorted_items()[0]['colspan'] == 1

        assert day1.rows[0].get_sorted_items()[1]['item'] == items[5]
        assert day1.rows[0].get_sorted_items()[1]['rowspan'] == 1
        assert day1.rows[0].get_sorted_items()[1]['colspan'] == 1

        assert day1.rows[1].get_sorted_items()[0]['item'] == items[1]
        assert day1.rows[1].get_sorted_items()[0]['rowspan'] == 1
        assert day1.rows[1].get_sorted_items()[0]['colspan'] == 1

        assert day1.rows[2].get_sorted_items()[1]['item'] == items[3]
        assert day1.rows[2].get_sorted_items()[1]['rowspan'] == 1
        assert day1.rows[2].get_sorted_items()[1]['colspan'] == 1

    def test_multiple_days(self):
        """Create a multiple day table with 3 slots and 2 venues and
           check we get the expected results"""
        # Schedule is
        #         Venue 1     Venue 2
        # ScheduleBlock1
        # 10-11   Item1       Item4
        # 11-12   Item2       Item5
        # ScheduleBlock2
        # 12-13   Item3       Item6
        day1 = ScheduleBlock.objects.create(
            start_time=D.datetime(2013, 9, 22, 7, 0, 0,
                                  tzinfo=timezone.utc),
            end_time=D.datetime(2013, 9, 22, 19, 0, 0,
                                tzinfo=timezone.utc),
            )
        day2 = ScheduleBlock.objects.create(
            start_time=D.datetime(2013, 9, 23, 7, 0, 0,
                                  tzinfo=timezone.utc),
            end_time=D.datetime(2013, 9, 23, 19, 0, 0,
                                tzinfo=timezone.utc),
            )
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue1.blocks.add(day1)
        venue1.blocks.add(day2)
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue2.blocks.add(day1)
        venue2.blocks.add(day2)

        start1 = D.datetime(2013, 9, 22, 10, 0, 0, tzinfo=timezone.utc)
        start2 = D.datetime(2013, 9, 22, 11, 0, 0, tzinfo=timezone.utc)
        end1 = D.datetime(2013, 9, 22, 12, 0, 0, tzinfo=timezone.utc)

        start3 = D.datetime(2013, 9, 23, 12, 0, 0, tzinfo=timezone.utc)
        end2 = D.datetime(2013, 9, 23, 13, 0, 0, tzinfo=timezone.utc)

        pages = make_pages(6)
        venues = [venue1, venue1, venue1, venue2, venue2, venue2]
        items = make_items(venues, pages)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2)
        slot2 = Slot.objects.create(start_time=start2, end_time=end1)
        slot3 = Slot.objects.create(start_time=start3, end_time=end2)

        items[0].slots.add(slot1)
        items[3].slots.add(slot1)
        items[1].slots.add(slot2)
        items[4].slots.add(slot2)
        items[2].slots.add(slot3)
        items[5].slots.add(slot3)

        c = Client()
        response = c.get('/schedule/')

        [day1, day2] = response.context['schedule_pages']

        assert len(day1.rows) == 2
        assert day1.venues == [venue1, venue2]
        assert len(day2.rows) == 1
        assert day2.venues == [venue1, venue2]
        assert day1.rows[0].slot.get_start_time() == start1
        assert day1.rows[0].slot.end_time == start2
        assert day1.rows[1].slot.get_start_time() == start2
        assert day1.rows[1].slot.end_time == end1
        assert day2.rows[0].slot.get_start_time() == start3
        assert day2.rows[0].slot.end_time == end2

        assert len(day1.rows[0].items) == 2
        assert len(day1.rows[1].items) == 2
        assert len(day2.rows[0].items) == 2

        assert day1.rows[0].get_sorted_items()[0]['item'] == items[0]
        assert day1.rows[0].get_sorted_items()[0]['rowspan'] == 1
        assert day1.rows[0].get_sorted_items()[0]['colspan'] == 1

        assert day2.rows[0].get_sorted_items()[1]['item'] == items[5]
        assert day2.rows[0].get_sorted_items()[1]['rowspan'] == 1
        assert day2.rows[0].get_sorted_items()[1]['colspan'] == 1

    def test_per_day_view(self):
        """Create a multiple day table with 3 slots and 2 venues and
           check we get the expected results using the per-day views"""
        # This is the same schedule as test_multiple_days
        block1 = ScheduleBlock.objects.create(
            start_time=D.datetime(2013, 9, 22, 7, 0, 0,
                                  tzinfo=timezone.utc),
            end_time=D.datetime(2013, 9, 22, 19, 0, 0,
                                tzinfo=timezone.utc),
            )
        block2 = ScheduleBlock.objects.create(
            start_time=D.datetime(2013, 9, 23, 7, 0, 0,
                                  tzinfo=timezone.utc),
            end_time=D.datetime(2013, 9, 23, 19, 0, 0,
                                tzinfo=timezone.utc),
            )
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue1.blocks.add(block1)
        venue1.blocks.add(block2)
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue2.blocks.add(block1)
        venue2.blocks.add(block2)

        start1 = D.datetime(2013, 9, 22, 10, 0, 0, tzinfo=timezone.utc)
        start2 = D.datetime(2013, 9, 22, 11, 0, 0, tzinfo=timezone.utc)
        end1 = D.datetime(2013, 9, 22, 12, 0, 0, tzinfo=timezone.utc)

        start3 = D.datetime(2013, 9, 23, 12, 0, 0, tzinfo=timezone.utc)
        end2 = D.datetime(2013, 9, 23, 13, 0, 0, tzinfo=timezone.utc)

        pages = make_pages(6)
        venues = [venue1, venue1, venue1, venue2, venue2, venue2]
        items = make_items(venues, pages)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2)
        slot2 = Slot.objects.create(start_time=start2, end_time=end1)
        slot3 = Slot.objects.create(start_time=start3, end_time=end2)

        items[0].slots.add(slot1)
        items[3].slots.add(slot1)
        items[1].slots.add(slot2)
        items[4].slots.add(slot2)
        items[2].slots.add(slot3)
        items[5].slots.add(slot3)

        c = Client()
        # Check that a wrong day gives the full schedule

        response = c.get('/schedule/?block=24')

        [day1, day2] = response.context['schedule_pages']

        self.assertEqual(len(day1.rows), 2)
        self.assertEqual(day1.venues, [venue1, venue2])
        self.assertEqual(len(day2.rows), 1)
        self.assertEqual(day2.venues, [venue1, venue2])
        self.assertEqual(day1.rows[0].slot.get_start_time(), start1)
        self.assertEqual(day1.rows[0].slot.end_time, start2)
        self.assertEqual(day1.rows[1].slot.get_start_time(), start2)
        self.assertEqual(day1.rows[1].slot.end_time, end1)
        self.assertEqual(day2.rows[0].slot.get_start_time(), start3)
        self.assertEqual(day2.rows[0].slot.end_time, end2)

        self.assertEqual(len(day1.rows[0].items), 2)
        self.assertEqual(len(day1.rows[1].items), 2)
        self.assertEqual(len(day2.rows[0].items), 2)

        self.assertEqual(day1.rows[0].get_sorted_items()[0]['item'], items[0])
        self.assertEqual(day1.rows[0].get_sorted_items()[0]['rowspan'], 1)
        self.assertEqual(day1.rows[0].get_sorted_items()[0]['colspan'], 1)

        self.assertEqual(day2.rows[0].get_sorted_items()[1]['item'], items[5])
        self.assertEqual(day2.rows[0].get_sorted_items()[1]['rowspan'], 1)
        self.assertEqual(day2.rows[0].get_sorted_items()[1]['colspan'], 1)

        # Test per-day schedule views
        response = c.get('/schedule/?block=%s' % block1.id)
        [day] = response.context['schedule_pages']

        self.assertEqual(day.block, day1.block)
        self.assertEqual(day.venues, day1.venues)
        self.assertEqual(len(day.rows), len(day1.rows))
        # Repeat a bunch of tests from the full schedule
        self.assertEqual(day.rows[0].slot.get_start_time(), start1)
        self.assertEqual(day.rows[0].slot.end_time, start2)
        self.assertEqual(len(day.rows[0].items), 2)
        self.assertEqual(len(day.rows[1].items), 2)
        self.assertEqual(day.rows[0].get_sorted_items()[0]['item'], items[0])
        self.assertEqual(day.rows[0].get_sorted_items()[0]['rowspan'], 1)
        self.assertEqual(day.rows[0].get_sorted_items()[0]['colspan'], 1)

        response = c.get('/schedule/?block=%d' % block2.id)
        [day] = response.context['schedule_pages']

        self.assertEqual(day.block, day2.block)
        self.assertEqual(day.venues, day2.venues)
        self.assertEqual(len(day.rows), len(day2.rows))
        # Repeat a bunch of tests from the full schedule
        self.assertEqual(day.rows[0].slot.get_start_time(), start3)
        self.assertEqual(day.rows[0].slot.end_time, end2)
        self.assertEqual(len(day.rows[0].items), 2)
        self.assertEqual(day.rows[0].get_sorted_items()[1]['item'], items[5])
        self.assertEqual(day.rows[0].get_sorted_items()[1]['rowspan'], 1)
        self.assertEqual(day.rows[0].get_sorted_items()[1]['colspan'], 1)

    def test_multiple_days_with_disjoint_venues(self):
        """Create a multiple day table with 3 slots and 2 venues and
           check we get the expected results"""
        # Schedule is
        # ScheduleBlock1
        #         Venue 1
        # 10-11   Item1
        # 11-12   Item2
        # ScheduleBlock2
        #         Venue 2
        # 12-13   Item3
        day1 = ScheduleBlock.objects.create(
            start_time=D.datetime(2013, 9, 22, 7, 0, 0,
                                  tzinfo=timezone.utc),
            end_time=D.datetime(2013, 9, 22, 19, 0, 0,
                                tzinfo=timezone.utc),
            )
        day2 = ScheduleBlock.objects.create(
            start_time=D.datetime(2013, 9, 23, 7, 0, 0,
                                  tzinfo=timezone.utc),
            end_time=D.datetime(2013, 9, 23, 19, 0, 0,
                                tzinfo=timezone.utc),
            )
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue1.blocks.add(day1)
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue2.blocks.add(day2)

        start1 = D.datetime(2013, 9, 22, 10, 0, 0, tzinfo=timezone.utc)
        start2 = D.datetime(2013, 9, 22, 11, 0, 0, tzinfo=timezone.utc)
        end1 = D.datetime(2013, 9, 22, 12, 0, 0, tzinfo=timezone.utc)

        start3 = D.datetime(2013, 9, 23, 12, 0, 0, tzinfo=timezone.utc)
        end2 = D.datetime(2013, 9, 23, 13, 0, 0, tzinfo=timezone.utc)

        pages = make_pages(3)
        venues = [venue1, venue1, venue2]
        items = make_items(venues, pages)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2)
        slot2 = Slot.objects.create(start_time=start2, end_time=end1)
        slot3 = Slot.objects.create(start_time=start3, end_time=end2)

        items[0].slots.add(slot1)
        items[1].slots.add(slot2)
        items[2].slots.add(slot3)

        c = Client()
        response = c.get('/schedule/')

        [day1, day2] = response.context['schedule_pages']

        assert len(day1.rows) == 2
        assert day1.venues == [venue1]
        assert len(day2.rows) == 1
        assert day2.venues == [venue2]
        assert day1.rows[0].slot.get_start_time() == start1
        assert day1.rows[0].slot.end_time == start2
        assert day1.rows[1].slot.get_start_time() == start2
        assert day1.rows[1].slot.end_time == end1
        assert day2.rows[0].slot.get_start_time() == start3
        assert day2.rows[0].slot.end_time == end2

        assert len(day1.rows[0].items) == 1
        assert len(day1.rows[1].items) == 1
        assert len(day2.rows[0].items) == 1

        assert day1.rows[0].get_sorted_items()[0]['item'] == items[0]
        assert day1.rows[0].get_sorted_items()[0]['rowspan'] == 1
        assert day1.rows[0].get_sorted_items()[0]['colspan'] == 1

        assert day2.rows[0].get_sorted_items()[0]['item'] == items[2]
        assert day2.rows[0].get_sorted_items()[0]['rowspan'] == 1
        assert day2.rows[0].get_sorted_items()[0]['colspan'] == 1

    def test_col_span(self):
        """Create table with 3 venues and some interesting
           venue spanning items"""
        # Schedule is
        #         Venue 1     Venue 2   Venue3
        # 10-11   Item0       --        Item6 +
        # 11-12   Item1 +     --        Item7 +
        # 12-13   Item2       --        Item8
        # 13-14   --          Item4 +   --
        # 14-15   Item3 +     Item5     --
        day1 = ScheduleBlock.objects.create(
            start_time=D.datetime(2013, 9, 22, 7, 0, 0,
                                  tzinfo=timezone.utc),
            end_time=D.datetime(2013, 9, 22, 19, 0, 0,
                                tzinfo=timezone.utc),
            )
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue3 = Venue.objects.create(order=3, name='Venue 3')
        venue1.blocks.add(day1)
        venue2.blocks.add(day1)
        venue3.blocks.add(day1)

        start1 = D.datetime(2013, 9, 22, 10, 0, 0, tzinfo=timezone.utc)
        start2 = D.datetime(2013, 9, 22, 11, 0, 0, tzinfo=timezone.utc)
        start3 = D.datetime(2013, 9, 22, 12, 0, 0, tzinfo=timezone.utc)
        start4 = D.datetime(2013, 9, 22, 13, 0, 0, tzinfo=timezone.utc)
        start5 = D.datetime(2013, 9, 22, 14, 0, 0, tzinfo=timezone.utc)
        end = D.datetime(2013, 9, 22, 15, 0, 0, tzinfo=timezone.utc)

        # We create the slots out of order to tt
        slot1 = Slot.objects.create(start_time=start1, end_time=start2)

        slot4 = Slot.objects.create(start_time=start4, end_time=start5)

        slot2 = Slot.objects.create(start_time=start2, end_time=start3)

        slot3 = Slot.objects.create(start_time=start3, end_time=start4)

        slot5 = Slot.objects.create(start_time=start5, end_time=end)

        pages = make_pages(10)
        venues = [venue1, venue1, venue1, venue1, venue2, venue2,
                  venue3, venue3, venue3]
        expand = [1, 3, 4, 6, 7]
        items = make_items(venues, pages, expand)

        items[0].slots.add(slot1)
        items[6].slots.add(slot1)
        items[1].slots.add(slot2)
        items[7].slots.add(slot2)
        items[2].slots.add(slot3)
        items[8].slots.add(slot3)
        items[4].slots.add(slot4)
        items[3].slots.add(slot5)
        items[5].slots.add(slot5)

        c = Client()
        response = c.get('/schedule/')

        [day1] = response.context['schedule_pages']

        assert len(day1.rows) == 5
        assert day1.venues == [venue1, venue2, venue3]
        assert day1.rows[0].slot.get_start_time() == start1
        assert day1.rows[1].slot.get_start_time() == start2
        assert day1.rows[2].slot.get_start_time() == start3
        assert day1.rows[3].slot.get_start_time() == start4
        assert day1.rows[4].slot.get_start_time() == start5

        assert len(day1.rows[0].items) == 2

        assert day1.rows[0].get_sorted_items()[0]['item'] == items[0]
        assert day1.rows[0].get_sorted_items()[0]['rowspan'] == 1
        assert day1.rows[0].get_sorted_items()[0]['colspan'] == 1

        assert day1.rows[0].get_sorted_items()[1]['item'] == items[6]
        assert day1.rows[0].get_sorted_items()[1]['rowspan'] == 1
        assert day1.rows[0].get_sorted_items()[1]['colspan'] == 2

        assert len(day1.rows[1].items) == 2

        assert day1.rows[1].get_sorted_items()[0]['item'] == items[1]
        assert day1.rows[1].get_sorted_items()[0]['rowspan'] == 1
        assert day1.rows[1].get_sorted_items()[0]['colspan'] == 2

        assert day1.rows[1].get_sorted_items()[1]['item'] == items[7]
        assert day1.rows[1].get_sorted_items()[1]['rowspan'] == 1
        assert day1.rows[1].get_sorted_items()[1]['colspan'] == 1

        assert len(day1.rows[2].items) == 3

        assert day1.rows[2].get_sorted_items()[0]['item'] == items[2]
        assert day1.rows[2].get_sorted_items()[0]['rowspan'] == 1
        assert day1.rows[2].get_sorted_items()[0]['colspan'] == 1

        assert day1.rows[2].get_sorted_items()[1]['item'] is None
        assert day1.rows[2].get_sorted_items()[1]['rowspan'] == 1
        assert day1.rows[2].get_sorted_items()[1]['colspan'] == 1

        assert day1.rows[2].get_sorted_items()[2]['item'] == items[8]
        assert day1.rows[2].get_sorted_items()[2]['rowspan'] == 1
        assert day1.rows[2].get_sorted_items()[2]['colspan'] == 1

        assert len(day1.rows[3].items) == 1

        assert day1.rows[3].get_sorted_items()[0]['item'] == items[4]
        assert day1.rows[3].get_sorted_items()[0]['rowspan'] == 1
        assert day1.rows[3].get_sorted_items()[0]['colspan'] == 3

        assert len(day1.rows[4].items) == 3

        assert day1.rows[4].get_sorted_items()[0]['item'] == items[3]
        assert day1.rows[4].get_sorted_items()[0]['rowspan'] == 1
        assert day1.rows[4].get_sorted_items()[0]['colspan'] == 1

        assert day1.rows[4].get_sorted_items()[1]['item'] == items[5]
        assert day1.rows[4].get_sorted_items()[1]['rowspan'] == 1
        assert day1.rows[4].get_sorted_items()[1]['colspan'] == 1

        assert day1.rows[4].get_sorted_items()[2]['item'] is None
        assert day1.rows[4].get_sorted_items()[2]['rowspan'] == 1
        assert day1.rows[4].get_sorted_items()[1]['colspan'] == 1

    def test_row_span(self):
        """Create a day table with multiple slot items"""
        # Schedule is
        #         Venue 1     Venue 2
        # 10-11   Item1       Item5
        # 11-12     |         Item6
        # 12-13   Item2       Item7
        # 13-14   Item3         |
        # 14-15   Item4         |
        day1 = ScheduleBlock.objects.create(
            start_time=D.datetime(2013, 9, 22, 7, 0, 0,
                                  tzinfo=timezone.utc),
            end_time=D.datetime(2013, 9, 22, 19, 0, 0,
                                tzinfo=timezone.utc),
            )
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue1.blocks.add(day1)
        venue2.blocks.add(day1)

        start1 = D.datetime(2013, 9, 22, 10, 0, 0, tzinfo=timezone.utc)
        start2 = D.datetime(2013, 9, 22, 11, 0, 0, tzinfo=timezone.utc)
        start3 = D.datetime(2013, 9, 22, 12, 0, 0, tzinfo=timezone.utc)
        start4 = D.datetime(2013, 9, 22, 13, 0, 0, tzinfo=timezone.utc)
        start5 = D.datetime(2013, 9, 22, 14, 0, 0, tzinfo=timezone.utc)
        end = D.datetime(2013, 9, 22, 15, 0, 0, tzinfo=timezone.utc)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2)
        slot2 = Slot.objects.create(start_time=start2, end_time=start3)
        slot3 = Slot.objects.create(start_time=start3, end_time=start4)
        slot4 = Slot.objects.create(start_time=start4, end_time=start5)
        slot5 = Slot.objects.create(start_time=start5, end_time=end)

        pages = make_pages(7)
        venues = [venue1, venue1, venue1, venue1, venue2, venue2, venue2]
        items = make_items(venues, pages)

        items[0].slots.add(slot1)
        items[0].slots.add(slot2)
        items[4].slots.add(slot1)
        items[5].slots.add(slot2)
        items[6].slots.add(slot3)
        items[6].slots.add(slot4)
        items[6].slots.add(slot5)
        items[1].slots.add(slot3)
        items[2].slots.add(slot4)
        items[3].slots.add(slot5)

        c = Client()
        response = c.get('/schedule/')

        [day1] = response.context['schedule_pages']

        assert len(day1.rows) == 5
        assert day1.venues == [venue1, venue2]
        assert day1.rows[0].slot.get_start_time() == start1
        assert day1.rows[1].slot.get_start_time() == start2
        assert day1.rows[4].slot.end_time == end

        assert len(day1.rows[0].items) == 2
        assert len(day1.rows[1].items) == 1
        assert len(day1.rows[2].items) == 2
        assert len(day1.rows[3].items) == 1
        assert len(day1.rows[4].items) == 1

        assert day1.rows[0].get_sorted_items()[0]['item'] == items[0]
        assert day1.rows[0].get_sorted_items()[0]['rowspan'] == 2
        assert day1.rows[0].get_sorted_items()[0]['colspan'] == 1

        assert day1.rows[0].get_sorted_items()[1]['item'] == items[4]
        assert day1.rows[0].get_sorted_items()[1]['rowspan'] == 1
        assert day1.rows[0].get_sorted_items()[1]['colspan'] == 1

        assert day1.rows[1].get_sorted_items()[0]['item'] == items[5]
        assert day1.rows[1].get_sorted_items()[0]['rowspan'] == 1
        assert day1.rows[1].get_sorted_items()[0]['colspan'] == 1

        assert day1.rows[2].get_sorted_items()[0]['item'] == items[1]
        assert day1.rows[2].get_sorted_items()[0]['rowspan'] == 1
        assert day1.rows[2].get_sorted_items()[0]['colspan'] == 1

        assert day1.rows[2].get_sorted_items()[1]['item'] == items[6]
        assert day1.rows[2].get_sorted_items()[1]['rowspan'] == 3
        assert day1.rows[2].get_sorted_items()[1]['colspan'] == 1

        assert day1.rows[3].get_sorted_items()[0]['item'] == items[2]
        assert day1.rows[3].get_sorted_items()[0]['rowspan'] == 1
        assert day1.rows[3].get_sorted_items()[0]['colspan'] == 1

        assert day1.rows[4].get_sorted_items()[0]['item'] == items[3]
        assert day1.rows[4].get_sorted_items()[0]['rowspan'] == 1
        assert day1.rows[4].get_sorted_items()[0]['colspan'] == 1

    def test_row_col_span(self):
        """Create table with 3 venues and both row & col
           venue spanning items"""
        # Schedule is
        #         Venue 1     Venue 2   Venue3
        # 10-11   Item0       --        Item5 +
        # 11-12   Item1 +     --        Item6 +
        # 12-13     |         --        Item7
        # 13-14   Item2 +     --          |
        # 14-15   Item3 +     Item4+     --
        day1 = ScheduleBlock.objects.create(
            start_time=D.datetime(2013, 9, 22, 7, 0, 0,
                                  tzinfo=timezone.utc),
            end_time=D.datetime(2013, 9, 22, 19, 0, 0,
                                tzinfo=timezone.utc),
            )
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue3 = Venue.objects.create(order=3, name='Venue 3')
        venue1.blocks.add(day1)
        venue2.blocks.add(day1)
        venue3.blocks.add(day1)

        start1 = D.datetime(2013, 9, 22, 10, 0, 0, tzinfo=timezone.utc)
        start2 = D.datetime(2013, 9, 22, 11, 0, 0, tzinfo=timezone.utc)
        start3 = D.datetime(2013, 9, 22, 12, 0, 0, tzinfo=timezone.utc)
        start4 = D.datetime(2013, 9, 22, 13, 0, 0, tzinfo=timezone.utc)
        start5 = D.datetime(2013, 9, 22, 14, 0, 0, tzinfo=timezone.utc)
        end = D.datetime(2013, 9, 22, 15, 0, 0, tzinfo=timezone.utc)

        # We create the slots out of order to tt
        slot1 = Slot.objects.create(start_time=start1, end_time=start2)
        slot4 = Slot.objects.create(start_time=start4, end_time=start5)
        slot2 = Slot.objects.create(start_time=start2, end_time=start3)
        slot3 = Slot.objects.create(start_time=start3, end_time=start4)
        slot5 = Slot.objects.create(start_time=start5, end_time=end)

        pages = make_pages(10)
        venues = [venue1, venue1, venue1, venue1, venue2,
                  venue3, venue3, venue3]
        expand = [1, 2, 3, 4, 5, 6]
        items = make_items(venues, pages, expand)

        items[0].slots.add(slot1)
        items[5].slots.add(slot1)
        items[1].slots.add(slot2)
        items[1].slots.add(slot3)
        items[6].slots.add(slot2)
        items[7].slots.add(slot3)
        items[7].slots.add(slot4)
        items[2].slots.add(slot4)
        items[3].slots.add(slot5)
        items[4].slots.add(slot5)

        c = Client()
        response = c.get('/schedule/')

        [day1] = response.context['schedule_pages']

        assert len(day1.rows) == 5
        assert day1.venues == [venue1, venue2, venue3]
        assert day1.rows[0].slot.get_start_time() == start1
        assert day1.rows[1].slot.get_start_time() == start2
        assert day1.rows[2].slot.get_start_time() == start3
        assert day1.rows[3].slot.get_start_time() == start4
        assert day1.rows[4].slot.get_start_time() == start5

        assert len(day1.rows[0].items) == 2

        assert day1.rows[0].get_sorted_items()[0]['item'] == items[0]
        assert day1.rows[0].get_sorted_items()[0]['rowspan'] == 1
        assert day1.rows[0].get_sorted_items()[0]['colspan'] == 1

        assert day1.rows[0].get_sorted_items()[1]['item'] == items[5]
        assert day1.rows[0].get_sorted_items()[1]['rowspan'] == 1
        assert day1.rows[0].get_sorted_items()[1]['colspan'] == 2

        assert len(day1.rows[1].items) == 2

        assert day1.rows[1].get_sorted_items()[0]['item'] == items[1]
        assert day1.rows[1].get_sorted_items()[0]['rowspan'] == 2
        assert day1.rows[1].get_sorted_items()[0]['colspan'] == 2

        assert day1.rows[1].get_sorted_items()[1]['item'] == items[6]
        assert day1.rows[1].get_sorted_items()[1]['rowspan'] == 1
        assert day1.rows[1].get_sorted_items()[1]['colspan'] == 1

        assert len(day1.rows[2].items) == 1

        assert day1.rows[2].get_sorted_items()[0]['item'] == items[7]
        assert day1.rows[2].get_sorted_items()[0]['rowspan'] == 2
        assert day1.rows[2].get_sorted_items()[0]['colspan'] == 1

        assert len(day1.rows[3].items) == 1

        assert day1.rows[3].get_sorted_items()[0]['item'] == items[2]
        assert day1.rows[3].get_sorted_items()[0]['rowspan'] == 1
        assert day1.rows[3].get_sorted_items()[0]['colspan'] == 2

        assert len(day1.rows[4].items) == 2

        assert day1.rows[4].get_sorted_items()[0]['item'] == items[3]
        assert day1.rows[4].get_sorted_items()[0]['rowspan'] == 1
        assert day1.rows[4].get_sorted_items()[0]['colspan'] == 1

        assert day1.rows[4].get_sorted_items()[1]['item'] == items[4]
        assert day1.rows[4].get_sorted_items()[1]['rowspan'] == 1
        assert day1.rows[4].get_sorted_items()[1]['colspan'] == 2

    def test_highlight_venue_view(self):
        """Test that the highlight-venue option works"""
        # This is the same schedule as test_multiple_days
        day1 = ScheduleBlock.objects.create(start_time=D.datetime(2013, 9, 22, 1, 0, 0,
                                                                  tzinfo=timezone.utc),
                                            end_time=D.datetime(2013, 9, 22, 23, 0, 0,
                                                                tzinfo=timezone.utc),
                                            )
        day2 = ScheduleBlock.objects.create(start_time=D.datetime(2013, 9, 23, 1, 0, 0,
                                                                  tzinfo=timezone.utc),
                                            end_time=D.datetime(2013, 9, 23, 23, 0, 0,
                                                                tzinfo=timezone.utc),
                                            )
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue1.blocks.add(day1)
        venue1.blocks.add(day2)
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue2.blocks.add(day1)
        venue2.blocks.add(day2)

        start1 = D.datetime(2013, 9, 22, 10, 0, 0, tzinfo=timezone.utc)
        start2 = D.datetime(2013, 9, 22, 11, 0, 0, tzinfo=timezone.utc)
        end1 = D.datetime(2013, 9, 22, 12, 0, 0, tzinfo=timezone.utc)

        start3 = D.datetime(2013, 9, 23, 12, 0, 0, tzinfo=timezone.utc)
        end2 = D.datetime(2013, 9, 23, 13, 0, 0, tzinfo=timezone.utc)

        pages = make_pages(6)
        venues = [venue1, venue1, venue1, venue2, venue2, venue2]
        items = make_items(venues, pages)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2)
        slot2 = Slot.objects.create(start_time=start2, end_time=end1)
        slot3 = Slot.objects.create(start_time=start3, end_time=end2)

        items[0].slots.add(slot1)
        items[3].slots.add(slot1)
        items[1].slots.add(slot2)
        items[4].slots.add(slot2)
        items[2].slots.add(slot3)
        items[5].slots.add(slot3)

        def validate_schedule(response):
            """Helper to ensure we aren't changing the schedule contents
               with the different parameters."""
            [day1, day2] = response.context['schedule_pages']

            self.assertEqual(len(day1.rows), 2)
            self.assertEqual(day1.venues, [venue1, venue2])
            self.assertEqual(len(day2.rows), 1)
            self.assertEqual(day2.venues, [venue1, venue2])
            self.assertEqual(day2.venues, [venue1, venue2])
            self.assertEqual(day1.rows[0].slot.get_start_time(), start1)
            self.assertEqual(day1.rows[0].slot.end_time, start2)
            self.assertEqual(day1.rows[1].slot.get_start_time(), start2)
            self.assertEqual(day1.rows[1].slot.end_time, end1)
            self.assertEqual(day2.rows[0].slot.get_start_time(), start3)
            self.assertEqual(day2.rows[0].slot.end_time, end2)

            self.assertEqual(len(day1.rows[0].items), 2)
            self.assertEqual(len(day1.rows[1].items), 2)
            self.assertEqual(len(day2.rows[0].items), 2)

        c = Client()

        # Check that we don't highlight anything if no venue is passed
        response = c.get('/schedule/')
        validate_schedule(response)

        self.assertNotContains(response, b'class="schedule-highlight-venue"')
        # Check that an invalid venue gives the entire schedule with no
        # 'schedule-highlight-venue' class
        response = c.get('/schedule/?highlight-venue=aaaaa')
        validate_schedule(response)

        self.assertNotContains(response, b'class="schedule-highlight-venue"')
        # Repeat the check for an invalid integer
        response = c.get('/schedule/?highlight-venue=%d' % (venue1.pk + venue2.pk))
        validate_schedule(response)
        self.assertNotContains(response, b'class="schedule-highlight-venue"')
        # Subset of the schedule checks, to make sure we look sane
        [day1, day2] = response.context['schedule_pages']

        self.assertEqual(len(day1.rows), 2)
        self.assertEqual(day1.venues, [venue1, venue2])
        self.assertEqual(len(day2.rows), 1)

        # Check that using a valid venue does have the string
        response = c.get('/schedule/?highlight-venue=%d' % venue1.pk)
        rendered = response.content
        self.assertContains(response, b'class="schedule-highlight-venue"')
        # Check that we haven't messed up the schedule content
        validate_schedule(response)
        # Check that we have the schedule-highlight-items in the right place
        t = '\n'.join(['<th class="schedule-highlight-venue"',
                       '<a href="/venue/%d/">' % venue1.pk,
                       venue1.name,
                       '</a></th>'])
        self.assertContains(response, '\n'.join(['<th class="schedule-highlight-venue">',
                                                 '<a href="%s">' % venue1.get_absolute_url(),
                                                 venue1.name,
                                                 '</a></th>']), html=True)
        self.assertContains(response, '\n'.join(['<th>',
                                                 '<a href="%s">' % venue2.get_absolute_url(),
                                                 venue2.name,
                                                 '</a></th>']), html=True)

        self.assertContains(response, '\n'.join([
            '<td colspan="1" rowspan="1" class="schedule schedule-highlight-venue">',
            '<a href="%s">' % items[0].get_url(),
            items[0].get_details(),
            '</a></td>']), html=True)
        self.assertContains(response, '\n'.join([
            '<td colspan="1" rowspan="1" class="schedule schedule-highlight-venue">',
            '<a href="%s">' % items[1].get_url(),
            items[1].get_details(),
            '</a></td>']), html=True)
        self.assertContains(response, '\n'.join([
            '<td colspan="1" rowspan="1" class="schedule schedule-highlight-venue">',
            '<a href="%s">' % items[2].get_url(),
            items[2].get_details(),
            '</a></td>']), html=True)
        self.assertContains(response, '\n'.join([
            '<td colspan="1" rowspan="1" class="schedule">',
            '<a href="%s">' % items[3].get_url(),
            items[3].get_details(),
            '</a></td>']), html=True)
        self.assertContains(response, '\n'.join([
            '<td colspan="1" rowspan="1" class="schedule">',
            '<a href="%s">' % items[5].get_url(),
            items[5].get_details(),
            '</a></td>']), html=True)
        # Check using venue2
        response = c.get('/schedule/?highlight-venue=%d' % venue2.pk)
        validate_schedule(response)
        self.assertContains(response, b'class="schedule-highlight-venue"')

        # Also check that the highlight tags are in the right place
        self.assertContains(response, '\n'.join(['<th>',
                                                 '<a href="%s">' % venue1.get_absolute_url(),
                                                 venue1.name,
                                                 '</a></th>']), html=True)
        self.assertContains(response, '\n'.join(['<th class="schedule-highlight-venue">',
                                                 '<a href="%s">' % venue2.get_absolute_url(),
                                                 venue2.name,
                                                 '</a></th>']), html=True)
        self.assertContains(response, '\n'.join([
            '<td colspan="1" rowspan="1" class="schedule schedule-highlight-venue">',
            '<a href="%s">' % items[3].get_url(),
            items[3].get_details(),
            '</a></td>']), html=True)
        self.assertContains(response, '\n'.join([
            '<td colspan="1" rowspan="1" class="schedule schedule-highlight-venue">',
            '<a href="%s">' % items[4].get_url(),
            items[4].get_details(),
            '</a></td>']), html=True)
        self.assertContains(response, '\n'.join([
            '<td colspan="1" rowspan="1" class="schedule schedule-highlight-venue">',
            '<a href="%s">' % items[5].get_url(),
            items[5].get_details(),
            '</a></td>']), html=True)
        self.assertContains(response, '\n'.join([
            '<td colspan="1" rowspan="1" class="schedule">',
            '<a href="%s">' % items[0].get_url(),
            items[0].get_details(),
            '</a></td>']), html=True)
        self.assertContains(response, '\n'.join([
            '<td colspan="1" rowspan="1" class="schedule">',
            '<a href="%s">' % items[2].get_url(),
            items[2].get_details(),
            '</a></td>']), html=True)


class CurrentViewTests(TestCase):

    def setUp(self):
        timezone.activate('UTC')

    def test_current_view_simple(self):
        """Create a schedule and check that the current view looks sane."""
        day1 = ScheduleBlock.objects.create(
            start_time=D.datetime(2013, 9, 22, 7, 0, 0,
                                  tzinfo=timezone.utc),
            end_time=D.datetime(2013, 9, 22, 19, 0, 0,
                                tzinfo=timezone.utc),
            )
        day2 = ScheduleBlock.objects.create(
            start_time=D.datetime(2013, 9, 23, 7, 0, 0,
                                  tzinfo=timezone.utc),
            end_time=D.datetime(2013, 9, 23, 19, 0, 0,
                                tzinfo=timezone.utc),
            )
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue1.blocks.add(day1)
        venue2.blocks.add(day1)

        start1 = D.datetime(2013, 9, 22, 10, 0, 0, tzinfo=timezone.utc)
        start2 = D.datetime(2013, 9, 22, 11, 0, 0, tzinfo=timezone.utc)
        start3 = D.datetime(2013, 9, 22, 12, 0, 0, tzinfo=timezone.utc)
        start4 = D.datetime(2013, 9, 22, 13, 0, 0, tzinfo=timezone.utc)
        start5 = D.datetime(2013, 9, 22, 14, 0, 0, tzinfo=timezone.utc)

        # During the first slot
        cur1 = D.datetime(2013, 9, 22, 10, 30, 0, tzinfo=timezone.utc)
        # Middle of the day
        cur2 = D.datetime(2013, 9, 22, 11, 30, 0, tzinfo=timezone.utc)
        cur3 = D.datetime(2013, 9, 22, 12, 30, 0, tzinfo=timezone.utc)
        # During the last slot
        cur4 = D.datetime(2013, 9, 22, 13, 30, 0, tzinfo=timezone.utc)
        # After the last slot
        cur5 = D.datetime(2013, 9, 22, 15, 30, 0, tzinfo=timezone.utc)

        slots = []

        slots.append(Slot.objects.create(start_time=start1, end_time=start2))
        slots.append(Slot.objects.create(start_time=start2, end_time=start3))
        slots.append(Slot.objects.create(start_time=start3, end_time=start4))
        slots.append(Slot.objects.create(start_time=start4, end_time=start5))

        pages = make_pages(8)
        venues = [venue1, venue2] * 4
        items = make_items(venues, pages)

        for index, item in enumerate(items):
            item.slots.add(slots[index // 2])

        c = Client()
        response = c.get('/schedule/current/',
                         {'day': day1.start_time.strftime('%Y-%m-%d'),
                          'time': cur1.strftime('%H:%M')})
        context = response.context

        assert context['cur_slot'] == slots[0]
        assert len(context['schedule_page'].venues) == 2
        # Only cur and next slot
        assert len(context['slots']) == 2
        assert context['slots'][0].items[venue1]['note'] == 'current'
        assert context['slots'][1].items[venue1]['note'] == 'forthcoming'

        response = c.get('/schedule/current/',
                         {'day': day1.start_time.strftime('%Y-%m-%d'),
                          'time': cur2.strftime('%H:%M')})
        context = response.context
        assert context['cur_slot'] == slots[1]
        assert len(context['schedule_page'].venues) == 2
        # prev, cur and next slot
        assert len(context['slots']) == 3
        assert context['slots'][0].items[venue1]['note'] == 'complete'
        assert context['slots'][1].items[venue1]['note'] == 'current'
        assert context['slots'][2].items[venue1]['note'] == 'forthcoming'

        response = c.get('/schedule/current/',
                         {'day': day1.start_time.strftime('%Y-%m-%d'),
                          'time': cur3.strftime('%H:%M')})
        context = response.context
        assert context['cur_slot'] == slots[2]
        assert len(context['schedule_page'].venues) == 2
        # prev and cur
        assert len(context['slots']) == 3
        assert context['slots'][0].items[venue1]['note'] == 'complete'
        assert context['slots'][1].items[venue1]['note'] == 'current'
        assert context['slots'][2].items[venue1]['note'] == 'forthcoming'

        response = c.get('/schedule/current/',
                         {'day': day1.start_time.strftime('%Y-%m-%d'),
                          'time': cur4.strftime('%H:%M')})
        context = response.context
        assert context['cur_slot'] == slots[3]
        assert len(context['schedule_page'].venues) == 2
        # preve and cur slot
        assert len(context['slots']) == 2
        assert context['slots'][0].items[venue1]['note'] == 'complete'
        assert context['slots'][1].items[venue1]['note'] == 'current'

        response = c.get('/schedule/current/',
                         {'day': day1.start_time.strftime('%Y-%m-%d'),
                          'time': cur5.strftime('%H:%M')})
        context = response.context
        assert context['cur_slot'] is None
        assert len(context['schedule_page'].venues) == 2
        # prev slot only
        assert len(context['slots']) == 1
        assert context['slots'][0].items[venue1]['note'] == 'complete'

        # Check that next day is an empty current view
        response = c.get('/schedule/current/',
                         {'day': day2.start_time.strftime('%Y-%m-%d'),
                          'time': cur3.strftime('%H:%M')})
        assert len(response.context['slots']) == 0

    def test_current_view_complex(self):
        """Create a schedule with overlapping venues and slotes and check that
           the current view looks sane."""
        # Schedule is
        #         Venue 1     Venue 2   Venue3
        # 10-11   Item1       --        Item5
        # 11-12   Item2       Item3     Item4
        # 12-13     |         Item7     Item6
        # 13-14   Item8         |         |
        # 14-15   --          Item9     Item10
        day1 = ScheduleBlock.objects.create(
            start_time=D.datetime(2013, 9, 22, 7, 0, 0,
                                  tzinfo=timezone.utc),
            end_time=D.datetime(2013, 9, 22, 19, 0, 0,
                                tzinfo=timezone.utc),
            )
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue3 = Venue.objects.create(order=3, name='Venue 3')
        venue1.blocks.add(day1)
        venue2.blocks.add(day1)
        venue3.blocks.add(day1)

        start1 = D.datetime(2013, 9, 22, 10, 0, 0, tzinfo=timezone.utc)
        start2 = D.datetime(2013, 9, 22, 11, 0, 0, tzinfo=timezone.utc)
        start3 = D.datetime(2013, 9, 22, 12, 0, 0, tzinfo=timezone.utc)
        start4 = D.datetime(2013, 9, 22, 13, 0, 0, tzinfo=timezone.utc)
        start5 = D.datetime(2013, 9, 22, 14, 0, 0, tzinfo=timezone.utc)
        end = D.datetime(2013, 9, 22, 15, 0, 0, tzinfo=timezone.utc)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2)
        slot2 = Slot.objects.create(start_time=start2, end_time=start3)
        slot3 = Slot.objects.create(start_time=start3, end_time=start4)
        slot4 = Slot.objects.create(start_time=start4, end_time=start5)
        slot5 = Slot.objects.create(start_time=start5, end_time=end)

        pages = make_pages(10)
        venues = [venue1, venue1, venue2, venue3, venue3, venue3,
                  venue2, venue1, venue2, venue3]
        items = make_items(venues, pages)

        items[0].slots.add(slot1)
        items[4].slots.add(slot1)
        items[1].slots.add(slot2)
        items[1].slots.add(slot3)
        items[2].slots.add(slot2)
        items[3].slots.add(slot2)
        items[5].slots.add(slot3)
        items[5].slots.add(slot4)
        items[6].slots.add(slot3)
        items[6].slots.add(slot4)
        items[7].slots.add(slot4)
        items[8].slots.add(slot5)
        items[9].slots.add(slot5)

        # During the first slot
        cur1 = D.datetime(2013, 9, 22, 10, 30, 0, tzinfo=timezone.utc)
        # Middle of the day
        cur2 = D.datetime(2013, 9, 22, 11, 30, 0, tzinfo=timezone.utc)
        cur3 = D.datetime(2013, 9, 22, 12, 30, 0, tzinfo=timezone.utc)
        # During the last slot
        cur4 = D.datetime(2013, 9, 22, 14, 30, 0, tzinfo=timezone.utc)

        c = Client()
        response = c.get('/schedule/current/',
                         {'day': day1.start_time.strftime('%Y-%m-%d'),
                          'time': cur1.strftime('%H:%M')})
        context = response.context
        assert context['cur_slot'] == slot1
        assert len(context['schedule_page'].venues) == 3
        assert len(context['slots']) == 2
        assert context['slots'][0].items[venue1]['note'] == 'current'
        assert context['slots'][0].items[venue1]['colspan'] == 1
        assert context['slots'][0].items[venue2]['item'] is None

        response = c.get('/schedule/current/',
                         {'day': day1.start_time.strftime('%Y-%m-%d'),
                          'time': cur2.strftime('%H:%M')})
        context = response.context
        assert context['cur_slot'] == slot2
        assert len(context['slots']) == 3
        assert context['slots'][0].items[venue1]['note'] == 'complete'
        assert context['slots'][1].items[venue1]['note'] == 'current'
        assert context['slots'][1].items[venue1]['rowspan'] == 2
        assert context['slots'][1].items[venue2]['note'] == 'current'
        assert context['slots'][1].items[venue2]['rowspan'] == 1
        # We truncate the rowspan for this event
        assert context['slots'][2].items[venue2]['note'] == 'forthcoming'
        assert context['slots'][2].items[venue2]['rowspan'] == 1

        response = c.get('/schedule/current/',
                         {'day': day1.start_time.strftime('%Y-%m-%d'),
                          'time': cur3.strftime('%H:%M')})
        context = response.context
        assert context['cur_slot'] == slot3
        assert len(context['slots']) == 3
        # This event is still current, even though it started last slot
        assert context['slots'][0].items[venue1]['note'] == 'current'
        assert context['slots'][0].items[venue1]['rowspan'] == 2
        # Venue 2 now has rowspan 2
        assert context['slots'][1].items[venue2]['note'] == 'current'
        assert context['slots'][1].items[venue2]['rowspan'] == 2

        response = c.get('/schedule/current/',
                         {'day': day1.start_time.strftime('%Y-%m-%d'),
                          'time': cur4.strftime('%H:%M')})
        context = response.context
        assert context['cur_slot'] == slot5
        assert len(context['slots']) == 2
        assert context['slots'][0].items[venue1]['note'] == 'complete'
        assert context['slots'][0].items[venue1]['rowspan'] == 1
        # Items are truncated to 1 row
        assert context['slots'][0].items[venue2]['note'] == 'complete'
        assert context['slots'][0].items[venue2]['rowspan'] == 1

    def test_current_view_highlight_venue(self):
        """Test that the current view highlight's stuff correctly"""
        day1 = ScheduleBlock.objects.create(start_time=D.datetime(2013, 9, 22, 7, 0, 0,
                                                                  tzinfo=timezone.utc),
                                            end_time=D.datetime(2013, 9, 22, 19, 0, 0,
                                                                tzinfo=timezone.utc),
                                            )
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue3 = Venue.objects.create(order=3, name='Venue 3')
        venue1.blocks.add(day1)
        venue2.blocks.add(day1)
        venue3.blocks.add(day1)

        start1 = D.datetime(2013, 9, 22, 10, 0, 0, tzinfo=timezone.utc)
        start2 = D.datetime(2013, 9, 22, 11, 0, 0, tzinfo=timezone.utc)
        start3 = D.datetime(2013, 9, 22, 12, 0, 0, tzinfo=timezone.utc)
        start4 = D.datetime(2013, 9, 22, 13, 0, 0, tzinfo=timezone.utc)
        start5 = D.datetime(2013, 9, 22, 14, 0, 0, tzinfo=timezone.utc)
        end = D.datetime(2013, 9, 22, 15, 0, 0, tzinfo=timezone.utc)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2)
        slot2 = Slot.objects.create(start_time=start2, end_time=start3)
        slot3 = Slot.objects.create(start_time=start3, end_time=start4)
        slot4 = Slot.objects.create(start_time=start4, end_time=start5)
        slot5 = Slot.objects.create(start_time=start5, end_time=end)

        pages = make_pages(10)
        venues = [venue1, venue1, venue2, venue3, venue3, venue3,
                  venue2, venue1, venue2, venue3]
        items = make_items(venues, pages)

        items[0].slots.add(slot1)
        items[4].slots.add(slot1)
        items[1].slots.add(slot2)
        items[1].slots.add(slot3)
        items[2].slots.add(slot2)
        items[3].slots.add(slot2)
        items[5].slots.add(slot3)
        items[5].slots.add(slot4)
        items[6].slots.add(slot3)
        items[6].slots.add(slot4)
        items[7].slots.add(slot4)
        items[8].slots.add(slot5)
        items[9].slots.add(slot5)

        # During the first slot
        cur1 = D.time(10, 30, 0)
        # Middle of the day
        cur2 = D.time(11, 30, 0)
        cur3 = D.time(12, 30, 0)
        # During the last slot
        cur4 = D.time(14, 30, 0)

        def validate_current(response):
            """Validate that the current view is still has the expected content"""
            context = response.context
            assert context['cur_slot'] == slot2
            assert len(context['slots']) == 3
            assert context['slots'][0].items[venue1]['note'] == 'complete'
            assert context['slots'][1].items[venue1]['note'] == 'current'
            assert context['slots'][1].items[venue1]['rowspan'] == 2
            assert context['slots'][1].items[venue2]['note'] == 'current'
            assert context['slots'][1].items[venue2]['rowspan'] == 1
            # We truncate the rowspan for this event
            assert context['slots'][2].items[venue2]['note'] == 'forthcoming'
            assert context['slots'][2].items[venue2]['rowspan'] == 1

        c = Client()
        # Check that we don't highlight if not asked
        response = c.get('/schedule/current/',
                         {'day': day1.start_time.strftime('%Y-%m-%d'),
                          'time': cur2.strftime('%H:%M')})
        validate_current(response)
        self.assertNotContains(response, b'schedule-highlight-venue')
        # Check with invalid venue
        response = c.get('/schedule/current/',
                         {'day': day1.start_time.strftime('%Y-%m-%d'),
                          'time': cur2.strftime('%H:%M'),
                          'highlight-venue': 'aaaa'})
        validate_current(response)
        self.assertNotContains(response, b'schedule-highlight-venue')

        # Check with venue 1
        response = c.get('/schedule/current/',
                         {'day': day1.start_time.strftime('%Y-%m-%d'),
                          'time': cur2.strftime('%H:%M'),
                          'highlight-venue': '%d' % venue1.pk})
        validate_current(response)
        self.assertContains(response, b'schedule-highlight-venue')
        self.assertContains(response, '\n'.join(['<th class="schedule-highlight-venue">',
                                                 '<a href="%s">' % venue1.get_absolute_url(),
                                                 venue1.name,
                                                 '</a></th>']), html=True)
        self.assertContains(response, '\n'.join(['<th>',
                                                 '<a href="%s">' % venue2.get_absolute_url(),
                                                 venue2.name,
                                                 '</a></th>']), html=True)
        self.assertContains(response, '\n'.join(['<th>',
                                                 '<a href="%s">' % venue3.get_absolute_url(),
                                                 venue3.name,
                                                 '</a></th>']), html=True)
        self.assertContains(response, '\n'.join([
            '<td colspan="1" rowspan="1" class="completed schedule-highlight-venue">',
            '<a href="%s">' % items[0].get_url(),
            items[0].get_details(),
            '</a></td>']), html=True)

        self.assertContains(response, '\n'.join([
            '<td colspan="1" rowspan="2" class="current_active schedule-highlight-venue">',
            '<a href="%s">' % items[1].get_url(),
            items[1].get_details(),
            '</a></td>']), html=True)

        self.assertContains(response, '\n'.join([
            '<td colspan="1" rowspan="1" class="completed">',
            '<a href="%s">' % items[4].get_url(),
            items[4].get_details(),
            '</a></td>']), html=True)

        self.assertContains(response, '\n'.join([
            '<td colspan="1" rowspan="1" class="current_active">',
            '<a href="%s">' % items[3].get_url(),
            items[3].get_details(),
            '</a></td>']), html=True)

        self.assertContains(response, '\n'.join([
            '<td colspan="1" rowspan="1" class="future">',
            '<a href="%s">' % items[5].get_url(),
            items[5].get_details(),
            '</a></td>']), html=True)

        # Check with venue 3
        response = c.get('/schedule/current/',
                         {'day': day1.start_time.strftime('%Y-%m-%d'),
                          'time': cur2.strftime('%H:%M'),
                          'highlight-venue': '%d' % venue3.pk})
        validate_current(response)
        self.assertContains(response, b'schedule-highlight-venue')

        self.assertContains(response, '\n'.join(['<th>',
                                                 '<a href="%s">' % venue1.get_absolute_url(),
                                                 venue1.name,
                                                 '</a></th>']), html=True)
        self.assertContains(response, '\n'.join(['<th>',
                                                 '<a href="%s">' % venue2.get_absolute_url(),
                                                 venue2.name,
                                                 '</a></th>']), html=True)
        self.assertContains(response, '\n'.join(['<th class="schedule-highlight-venue">',
                                                 '<a href="%s">' % venue3.get_absolute_url(),
                                                 venue3.name,
                                                 '</a></th>']), html=True)
        self.assertContains(response, '\n'.join([
            '<td colspan="1" rowspan="1" class="completed">',
            '<a href="%s">' % items[0].get_url(),
            items[0].get_details(),
            '</a></td>']), html=True)

        self.assertContains(response, '\n'.join([
            '<td colspan="1" rowspan="2" class="current_active">',
            '<a href="%s">' % items[1].get_url(),
            items[1].get_details(),
            '</a></td>']), html=True)

        self.assertContains(response, '\n'.join([
            '<td colspan="1" rowspan="1" class="completed schedule-highlight-venue">',
            '<a href="%s">' % items[4].get_url(),
            items[4].get_details(),
            '</a></td>']), html=True)

        self.assertContains(response, '\n'.join([
            '<td colspan="1" rowspan="1" class="current_active schedule-highlight-venue">',
            '<a href="%s">' % items[3].get_url(),
            items[3].get_details(),
            '</a></td>']), html=True)

        self.assertContains(response, '\n'.join([
            '<td colspan="1" rowspan="1" class="future schedule-highlight-venue">',
            '<a href="%s">' % items[5].get_url(),
            items[5].get_details(),
            '</a></td>']), html=True)

    def test_current_view_invalid(self):
        """Test that invalid schedules return a inactive current view."""
        day1 = ScheduleBlock.objects.create(
            start_time=D.datetime(2013, 9, 22, 7, 0, 0,
                                  tzinfo=timezone.utc),
            end_time=D.datetime(2013, 9, 22, 19, 0, 0,
                                tzinfo=timezone.utc),
            )
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue1.blocks.add(day1)
        start1 = D.datetime(2013, 9, 22, 10, 0, 0, tzinfo=timezone.utc)
        start2 = D.datetime(2013, 9, 22, 11, 0, 0, tzinfo=timezone.utc)
        end = D.datetime(2013, 9, 22, 12, 0, 0, tzinfo=timezone.utc)
        cur1 = D.datetime(2013, 9, 22, 10, 30, 0, tzinfo=timezone.utc)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2)
        slot2 = Slot.objects.create(start_time=start1, end_time=end)

        user = get_user_model().objects.create_user('john', 'best@wafer.test',
                                                    'johnpassword')
        talk = Talk.objects.create(title="Test talk", status=ACCEPTED,
                                   corresponding_author_id=user.id)

        item1 = ScheduleItem.objects.create(venue=venue1,
                                            talk_id=talk.pk)
        item1.slots.add(slot1)
        item2 = ScheduleItem.objects.create(venue=venue1,
                                            talk_id=talk.pk)
        item2.slots.add(slot2)

        c = Client()
        response = c.get('/schedule/current/',
                         {'day': day1.start_time.strftime('%Y-%m-%d'),
                          'time': cur1.strftime('%H:%M')})
        assert response.context['active'] is False


class NonHTMLViewTests(TestCase):

    def setUp(self):
        # Create the schedule used for these tests
        timezone.activate('UTC')
        day1 = ScheduleBlock.objects.create(
            start_time=D.datetime(2013, 9, 22, 7, 0, 0,
                                  tzinfo=timezone.utc),
            end_time=D.datetime(2013, 9, 22, 19, 0, 0,
                                tzinfo=timezone.utc),
            )
        day2 = ScheduleBlock.objects.create(
            start_time=D.datetime(2013, 9, 23, 7, 0, 0,
                                  tzinfo=timezone.utc),
            end_time=D.datetime(2013, 9, 23, 19, 0, 0,
                                tzinfo=timezone.utc),
            )
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue1.blocks.add(day1)
        venue2.blocks.add(day1)

        start1 = D.datetime(2013, 9, 22, 10, 0, 0, tzinfo=timezone.utc)
        start2 = D.datetime(2013, 9, 22, 11, 0, 0, tzinfo=timezone.utc)
        start3 = D.datetime(2013, 9, 22, 12, 0, 0, tzinfo=timezone.utc)
        start4 = D.datetime(2013, 9, 22, 13, 0, 0, tzinfo=timezone.utc)
        start5 = D.datetime(2013, 9, 22, 14, 0, 0, tzinfo=timezone.utc)

        slots = []

        slots.append(Slot.objects.create(start_time=start1, end_time=start2))
        slots.append(Slot.objects.create(start_time=start2, end_time=start3))
        slots.append(Slot.objects.create(start_time=start3, end_time=start4))
        slots.append(Slot.objects.create(start_time=start4, end_time=start5))

        pages = make_pages(8)
        venues = [venue1, venue2] * 4
        items = make_items(venues, pages)

        for index, item in enumerate(items):
            item.slots.add(slots[index // 2])

    def test_pentabarf_view(self):
        # We don't exhaustively test that the pentabarf view is valid pentabarf,
        # instead we test that the XML is valid, and that we
        # have the basic details we expect present
        c = Client()
        response = c.get('/schedule/pentabarf.xml')
        parsed = ElementTree.XML(response.content)
        self.assertEqual(parsed.tag, 'schedule')
        self.assertEqual(parsed[0].tag, 'conference')
        self.assertEqual(parsed[1].tag, 'day')

        day = parsed[1]
        self.assertIn(('date', '2013-09-22'), day.items())
        self.assertEqual(day[0].tag, 'room')
        self.assertIn(('name', 'Venue 1'), day[0].items())
        talk = day[0][0]
        self.assertEqual(talk[0].tag, 'date')
        self.assertEqual(talk[0].text, '2013-09-22T10:00:00+00:00')
        title = [z for z in talk if z.tag == 'title'][0]
        self.assertEqual(title.text, 'Item 0')

    def test_ics_view(self):
        # This is a bit circular, since we use icalendar to generate
        # the data, but does test we can at least parse the generated
        # file, and that we are including the right number of events
        # and some of the required details
        c = Client()
        response = c.get('/schedule/schedule.ics')
        calendar = icalendar.Calendar.from_ical(response.content)
        # No major errors
        self.assertFalse(calendar.is_broken)
        # Check number of events
        self.assertEqual(len(calendar.walk(name='VEVENT')), 8)
        # Check we have the right time in places
        event = calendar.walk(name='VEVENT')[0]
        self.assertEqual(event['dtstart'].params['value'], 'DATE-TIME')
        self.assertEqual(event['dtstart'].dt, D.datetime(2013, 9, 22, 10, 0, 0, tzinfo=timezone.utc))


class ScheduleItemViewSetTests(TestCase):

    def setUp(self):
        timezone.activate('UTC')

    def test_unauthorized_users_are_forbidden(self):
        c = create_client('ordinary', superuser=False)
        response = c.get('/schedule/api/scheduleitems/')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {
            "detail": "You do not have permission to perform this action.",
        })

    def test_list_scheduleitems(self):
        venue = make_venue()
        [page] = make_pages(1)
        [item] = make_items([venue], [page])
        slot = make_slot()
        item.slots.add(slot)
        c = create_client('super', superuser=True)
        response = c.get('/schedule/api/scheduleitems/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [{
                "id": item.pk,
                "venue": venue.pk,
                "slots": [slot.pk],
                "page": page.pk,
                "talk": None,
            }],
        })

    def test_create_scheduleitem(self):
        venue = make_venue()
        slot = make_slot()
        [page] = make_pages(1)
        c = create_client('super', superuser=True)
        response = c.post(
            '/schedule/api/scheduleitems/',
            data=json.dumps({
                "venue": venue.pk,
                "slots": [slot.pk],
                "page": page.pk,
                "talk": '',
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 201)
        [item] = ScheduleItem.objects.all()
        self.assertEqual(response.data, {
            'id': item.pk,
            'venue': venue.pk,
            'slots': [slot.pk],
            'talk': None,
            'page': page.pk,
        })

    def test_put_scheduleitem(self):
        venue = make_venue()
        slot = make_slot()
        [page] = make_pages(1)
        [item] = make_items([venue], [page])
        slot = make_slot()
        c = create_client('super', superuser=True)
        response = c.put(
            '/schedule/api/scheduleitems/%s/' % item.pk, data=json.dumps({
                "venue": venue.pk,
                "slots": [slot.pk],
                "page": page.pk,
                "talk": '',
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            'id': item.pk,
            'venue': venue.pk,
            'slots': [slot.pk],
            'talk': None,
            'page': page.pk,
        })

    def test_patch_scheduleitem(self):
        venue = make_venue()
        slot = make_slot()
        [page] = make_pages(1)
        [item] = make_items([venue], [page])
        slot = make_slot()
        c = create_client('super', superuser=True)
        response = c.patch(
            '/schedule/api/scheduleitems/%s/' % item.pk, data=json.dumps({
                "slots": [slot.pk],
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            'id': item.pk,
            'venue': venue.pk,
            'slots': [slot.pk],
            'talk': None,
            'page': page.pk,
        })

    def test_delete_scheduleitem(self):
        venue = make_venue()
        [page] = make_pages(1)
        [item] = make_items([venue], [page])
        c = create_client('super', superuser=True)
        response = c.delete(
            '/schedule/api/scheduleitems/%s/' % item.pk)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, None)
        self.assertEqual(ScheduleItem.objects.count(), 0)
