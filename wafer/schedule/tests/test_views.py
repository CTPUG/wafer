import json
import datetime as D
import icalendar
from xml.etree import ElementTree

from django.test import Client, TestCase
from django.contrib.auth import get_user_model

from wafer.talks.models import Talk, ACCEPTED
from wafer.pages.models import Page
from wafer.schedule.models import Day, Venue, Slot, ScheduleItem
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
    day = Day.objects.create(date=D.date(2013, 9, 22))
    start = D.time(10, 0, 0)
    end = D.time(15, 0, 0)
    slot = Slot.objects.create(start_time=start, end_time=end,
                               day=day)
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
    def test_simple_table(self):
        """Create a simple, single day table with 3 slots and 2 venues and
           check we get the expected results"""

        # Schedule is
        #         Venue 1     Venue 2
        # 10-11   Item1       Item4
        # 11-12   Item2       Item5
        # 12-13   Item3       Item6
        day1 = Day.objects.create(date=D.date(2013, 9, 22))

        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue1.days.add(day1)
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue2.days.add(day1)

        start1 = D.time(10, 0, 0)
        start2 = D.time(11, 0, 0)
        start3 = D.time(12, 0, 0)
        end = D.time(13, 0, 0)

        pages = make_pages(6)
        venues = [venue1, venue1, venue1, venue2, venue2, venue2]
        items = make_items(venues, pages)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2,
                                    day=day1)
        slot2 = Slot.objects.create(previous_slot=slot1, end_time=start3,
                                    day=day1)
        slot3 = Slot.objects.create(previous_slot=slot2, end_time=end,
                                    day=day1)

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

        [day1] = response.context['schedule_days']

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
        day1 = Day.objects.create(date=D.date(2013, 9, 22))
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue1.days.add(day1)
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue2.days.add(day1)

        start1 = D.time(10, 0, 0)
        start2 = D.time(11, 0, 0)
        start3 = D.time(12, 0, 0)
        end = D.time(13, 0, 0)

        pages = make_pages(6)
        venues = [venue1, venue1, venue1, venue2, venue2, venue2]
        items = make_items(venues, pages)

        # Create the slots not in date order either

        slot1 = Slot.objects.create(start_time=start1, end_time=start2,
                                    day=day1)
        slot3 = Slot.objects.create(previous_slot=slot1, end_time=end,
                                    day=day1)
        slot2 = Slot.objects.create(previous_slot=slot1, end_time=start3,
                                    day=day1)
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

        [day1] = response.context['schedule_days']

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
        # Day1
        # 10-11   Item1       Item4
        # 11-12   Item2       Item5
        # Day2
        # 12-13   Item3       Item6
        day1 = Day.objects.create(date=D.date(2013, 9, 22))
        day2 = Day.objects.create(date=D.date(2013, 9, 23))
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue1.days.add(day1)
        venue1.days.add(day2)
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue2.days.add(day1)
        venue2.days.add(day2)

        start1 = D.time(10, 0, 0)
        start2 = D.time(11, 0, 0)
        end1 = D.time(12, 0, 0)

        start3 = D.time(12, 0, 0)
        end2 = D.time(13, 0, 0)

        pages = make_pages(6)
        venues = [venue1, venue1, venue1, venue2, venue2, venue2]
        items = make_items(venues, pages)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2,
                                    day=day1)
        slot2 = Slot.objects.create(start_time=start2, end_time=end1,
                                    day=day1)
        slot3 = Slot.objects.create(start_time=start3, end_time=end2,
                                    day=day2)

        items[0].slots.add(slot1)
        items[3].slots.add(slot1)
        items[1].slots.add(slot2)
        items[4].slots.add(slot2)
        items[2].slots.add(slot3)
        items[5].slots.add(slot3)

        c = Client()
        response = c.get('/schedule/')

        [day1, day2] = response.context['schedule_days']

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
        day1 = Day.objects.create(date=D.date(2013, 9, 22))
        day2 = Day.objects.create(date=D.date(2013, 9, 23))
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue1.days.add(day1)
        venue1.days.add(day2)
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue2.days.add(day1)
        venue2.days.add(day2)

        start1 = D.time(10, 0, 0)
        start2 = D.time(11, 0, 0)
        end1 = D.time(12, 0, 0)

        start3 = D.time(12, 0, 0)
        end2 = D.time(13, 0, 0)

        pages = make_pages(6)
        venues = [venue1, venue1, venue1, venue2, venue2, venue2]
        items = make_items(venues, pages)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2,
                                    day=day1)
        slot2 = Slot.objects.create(start_time=start2, end_time=end1,
                                    day=day1)
        slot3 = Slot.objects.create(start_time=start3, end_time=end2,
                                    day=day2)

        items[0].slots.add(slot1)
        items[3].slots.add(slot1)
        items[1].slots.add(slot2)
        items[4].slots.add(slot2)
        items[2].slots.add(slot3)
        items[5].slots.add(slot3)

        c = Client()
        # Check that a wrong day gives the full schedule

        response = c.get('/schedule/?day=2013-09-24')

        [day1, day2] = response.context['schedule_days']

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
        response = c.get('/schedule/?day=2013-09-22')
        [day] = response.context['schedule_days']

        self.assertEqual(day.day, day1.day)
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

        response = c.get('/schedule/?day=2013-09-23')
        [day] = response.context['schedule_days']

        self.assertEqual(day.day, day2.day)
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
        # Day1
        #         Venue 1
        # 10-11   Item1
        # 11-12   Item2
        # Day2
        #         Venue 2
        # 12-13   Item3
        day1 = Day.objects.create(date=D.date(2013, 9, 22))
        day2 = Day.objects.create(date=D.date(2013, 9, 23))
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue1.days.add(day1)
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue2.days.add(day2)

        start1 = D.time(10, 0, 0)
        start2 = D.time(11, 0, 0)
        end1 = D.time(12, 0, 0)

        start3 = D.time(12, 0, 0)
        end2 = D.time(13, 0, 0)

        pages = make_pages(3)
        venues = [venue1, venue1, venue2]
        items = make_items(venues, pages)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2,
                                    day=day1)
        slot2 = Slot.objects.create(start_time=start2, end_time=end1,
                                    day=day1)
        slot3 = Slot.objects.create(start_time=start3, end_time=end2,
                                    day=day2)

        items[0].slots.add(slot1)
        items[1].slots.add(slot2)
        items[2].slots.add(slot3)

        c = Client()
        response = c.get('/schedule/')

        [day1, day2] = response.context['schedule_days']

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
        day1 = Day.objects.create(date=D.date(2013, 9, 22))
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue3 = Venue.objects.create(order=3, name='Venue 3')
        venue1.days.add(day1)
        venue2.days.add(day1)
        venue3.days.add(day1)

        start1 = D.time(10, 0, 0)
        start2 = D.time(11, 0, 0)
        start3 = D.time(12, 0, 0)
        start4 = D.time(13, 0, 0)
        start5 = D.time(14, 0, 0)
        end = D.time(15, 0, 0)

        # We create the slots out of order to tt
        slot1 = Slot.objects.create(start_time=start1, end_time=start2,
                                    day=day1)

        slot4 = Slot.objects.create(start_time=start4, end_time=start5,
                                    day=day1)

        slot2 = Slot.objects.create(start_time=start2, end_time=start3,
                                    day=day1)

        slot3 = Slot.objects.create(start_time=start3, end_time=start4,
                                    day=day1)

        slot5 = Slot.objects.create(start_time=start5, end_time=end,
                                    day=day1)

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

        [day1] = response.context['schedule_days']

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
        day1 = Day.objects.create(date=D.date(2013, 9, 22))
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue1.days.add(day1)
        venue2.days.add(day1)

        start1 = D.time(10, 0, 0)
        start2 = D.time(11, 0, 0)
        start3 = D.time(12, 0, 0)
        start4 = D.time(13, 0, 0)
        start5 = D.time(14, 0, 0)
        end = D.time(15, 0, 0)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2,
                                    day=day1)
        slot2 = Slot.objects.create(start_time=start2, end_time=start3,
                                    day=day1)
        slot3 = Slot.objects.create(start_time=start3, end_time=start4,
                                    day=day1)
        slot4 = Slot.objects.create(start_time=start4, end_time=start5,
                                    day=day1)
        slot5 = Slot.objects.create(start_time=start5, end_time=end,
                                    day=day1)

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

        [day1] = response.context['schedule_days']

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
        day1 = Day.objects.create(date=D.date(2013, 9, 22))
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue3 = Venue.objects.create(order=3, name='Venue 3')
        venue1.days.add(day1)
        venue2.days.add(day1)
        venue3.days.add(day1)

        start1 = D.time(10, 0, 0)
        start2 = D.time(11, 0, 0)
        start3 = D.time(12, 0, 0)
        start4 = D.time(13, 0, 0)
        start5 = D.time(14, 0, 0)
        end = D.time(15, 0, 0)

        # We create the slots out of order to tt
        slot1 = Slot.objects.create(start_time=start1, end_time=start2,
                                    day=day1)

        slot4 = Slot.objects.create(start_time=start4, end_time=start5,
                                    day=day1)

        slot2 = Slot.objects.create(start_time=start2, end_time=start3,
                                    day=day1)

        slot3 = Slot.objects.create(start_time=start3, end_time=start4,
                                    day=day1)

        slot5 = Slot.objects.create(start_time=start5, end_time=end,
                                    day=day1)

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

        [day1] = response.context['schedule_days']

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


class CurrentViewTests(TestCase):
    def test_current_view_simple(self):
        """Create a schedule and check that the current view looks sane."""
        day1 = Day.objects.create(date=D.date(2013, 9, 22))
        day2 = Day.objects.create(date=D.date(2013, 9, 23))
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue1.days.add(day1)
        venue2.days.add(day1)

        start1 = D.time(10, 0, 0)
        start2 = D.time(11, 0, 0)
        start3 = D.time(12, 0, 0)
        start4 = D.time(13, 0, 0)
        start5 = D.time(14, 0, 0)

        # During the first slot
        cur1 = D.time(10, 30, 0)
        # Middle of the day
        cur2 = D.time(11, 30, 0)
        cur3 = D.time(12, 30, 0)
        # During the last slot
        cur4 = D.time(13, 30, 0)
        # After the last slot
        cur5 = D.time(15, 30, 0)

        slots = []

        slots.append(Slot.objects.create(start_time=start1, end_time=start2,
                                         day=day1))
        slots.append(Slot.objects.create(start_time=start2, end_time=start3,
                                         day=day1))
        slots.append(Slot.objects.create(start_time=start3, end_time=start4,
                                         day=day1))
        slots.append(Slot.objects.create(start_time=start4, end_time=start5,
                                         day=day1))

        pages = make_pages(8)
        venues = [venue1, venue2] * 4
        items = make_items(venues, pages)

        for index, item in enumerate(items):
            item.slots.add(slots[index // 2])

        c = Client()
        response = c.get('/schedule/current/',
                         {'day': day1.date.strftime('%Y-%m-%d'),
                          'time': cur1.strftime('%H:%M')})
        context = response.context

        assert context['cur_slot'] == slots[0]
        assert len(context['schedule_day'].venues) == 2
        # Only cur and next slot
        assert len(context['slots']) == 2
        assert context['slots'][0].items[venue1]['note'] == 'current'
        assert context['slots'][1].items[venue1]['note'] == 'forthcoming'

        response = c.get('/schedule/current/',
                         {'day': day1.date.strftime('%Y-%m-%d'),
                          'time': cur2.strftime('%H:%M')})
        context = response.context
        assert context['cur_slot'] == slots[1]
        assert len(context['schedule_day'].venues) == 2
        # prev, cur and next slot
        assert len(context['slots']) == 3
        assert context['slots'][0].items[venue1]['note'] == 'complete'
        assert context['slots'][1].items[venue1]['note'] == 'current'
        assert context['slots'][2].items[venue1]['note'] == 'forthcoming'

        response = c.get('/schedule/current/',
                         {'day': day1.date.strftime('%Y-%m-%d'),
                          'time': cur3.strftime('%H:%M')})
        context = response.context
        assert context['cur_slot'] == slots[2]
        assert len(context['schedule_day'].venues) == 2
        # prev and cur
        assert len(context['slots']) == 3
        assert context['slots'][0].items[venue1]['note'] == 'complete'
        assert context['slots'][1].items[venue1]['note'] == 'current'
        assert context['slots'][2].items[venue1]['note'] == 'forthcoming'

        response = c.get('/schedule/current/',
                         {'day': day1.date.strftime('%Y-%m-%d'),
                          'time': cur4.strftime('%H:%M')})
        context = response.context
        assert context['cur_slot'] == slots[3]
        assert len(context['schedule_day'].venues) == 2
        # preve and cur slot
        assert len(context['slots']) == 2
        assert context['slots'][0].items[venue1]['note'] == 'complete'
        assert context['slots'][1].items[venue1]['note'] == 'current'

        response = c.get('/schedule/current/',
                         {'day': day1.date.strftime('%Y-%m-%d'),
                          'time': cur5.strftime('%H:%M')})
        context = response.context
        assert context['cur_slot'] is None
        assert len(context['schedule_day'].venues) == 2
        # prev slot only
        assert len(context['slots']) == 1
        assert context['slots'][0].items[venue1]['note'] == 'complete'

        # Check that next day is an empty current view
        response = c.get('/schedule/current/',
                         {'day': day2.date.strftime('%Y-%m-%d'),
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
        day1 = Day.objects.create(date=D.date(2013, 9, 22))
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue3 = Venue.objects.create(order=3, name='Venue 3')
        venue1.days.add(day1)
        venue2.days.add(day1)
        venue3.days.add(day1)

        start1 = D.time(10, 0, 0)
        start2 = D.time(11, 0, 0)
        start3 = D.time(12, 0, 0)
        start4 = D.time(13, 0, 0)
        start5 = D.time(14, 0, 0)
        end = D.time(15, 0, 0)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2,
                                    day=day1)
        slot2 = Slot.objects.create(start_time=start2, end_time=start3,
                                    day=day1)
        slot3 = Slot.objects.create(start_time=start3, end_time=start4,
                                    day=day1)
        slot4 = Slot.objects.create(start_time=start4, end_time=start5,
                                    day=day1)
        slot5 = Slot.objects.create(start_time=start5, end_time=end,
                                    day=day1)

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

        c = Client()
        response = c.get('/schedule/current/',
                         {'day': day1.date.strftime('%Y-%m-%d'),
                          'time': cur1.strftime('%H:%M')})
        context = response.context
        assert context['cur_slot'] == slot1
        assert len(context['schedule_day'].venues) == 3
        assert len(context['slots']) == 2
        assert context['slots'][0].items[venue1]['note'] == 'current'
        assert context['slots'][0].items[venue1]['colspan'] == 1
        assert context['slots'][0].items[venue2]['item'] is None

        response = c.get('/schedule/current/',
                         {'day': day1.date.strftime('%Y-%m-%d'),
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
                         {'day': day1.date.strftime('%Y-%m-%d'),
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
                         {'day': day1.date.strftime('%Y-%m-%d'),
                          'time': cur4.strftime('%H:%M')})
        context = response.context
        assert context['cur_slot'] == slot5
        assert len(context['slots']) == 2
        assert context['slots'][0].items[venue1]['note'] == 'complete'
        assert context['slots'][0].items[venue1]['rowspan'] == 1
        # Items are truncated to 1 row
        assert context['slots'][0].items[venue2]['note'] == 'complete'
        assert context['slots'][0].items[venue2]['rowspan'] == 1

    def test_current_view_invalid(self):
        """Test that invalid schedules return a inactive current view."""
        day1 = Day.objects.create(date=D.date(2013, 9, 22))
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue1.days.add(day1)
        start1 = D.time(10, 0, 0)
        start2 = D.time(11, 0, 0)
        end = D.time(12, 0, 0)
        cur1 = D.time(10, 30, 0)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2,
                                    day=day1)
        slot2 = Slot.objects.create(start_time=start1, end_time=end,
                                    day=day1)

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
                         {'day': day1.date.strftime('%Y-%m-%d'),
                          'time': cur1.strftime('%H:%M')})
        assert response.context['active'] is False


class NonHTMLViewTests(TestCase):

    def setUp(self):
        # Create the schedule used for these tests
        day1 = Day.objects.create(date=D.date(2013, 9, 22))
        day2 = Day.objects.create(date=D.date(2013, 9, 23))
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue1.days.add(day1)
        venue2.days.add(day1)

        start1 = D.time(10, 0, 0)
        start2 = D.time(11, 0, 0)
        start3 = D.time(12, 0, 0)
        start4 = D.time(13, 0, 0)
        start5 = D.time(14, 0, 0)

        slots = []

        slots.append(Slot.objects.create(start_time=start1, end_time=start2,
                                         day=day1))
        slots.append(Slot.objects.create(start_time=start2, end_time=start3,
                                         day=day1))
        slots.append(Slot.objects.create(start_time=start3, end_time=start4,
                                         day=day1))
        slots.append(Slot.objects.create(start_time=start4, end_time=start5,
                                         day=day1))

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
        self.assertEqual(event['dtstart'].dt, D.datetime(2013, 9, 22, 10, 0, 0))


class ScheduleItemViewSetTests(TestCase):
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
