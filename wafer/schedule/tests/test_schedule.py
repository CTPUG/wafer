from django.test import Client, TestCase
from django.utils.timezone import utc

import datetime as D
from wafer.schedule.models import Venue, Slot, ScheduleItem


class ScheduleTests(TestCase):

    def test_venue_list(self):
        """Create venues and check that we get the expected list back"""
        Venue.objects.create(order=2, name='Venue 2')
        Venue.objects.create(order=1, name='Venue 1')

        assert Venue.objects.count() == 2

        c = Client()
        response = c.get('/schedule/')

        assert len(response.context['venue_list']) == 2
        assert response.context["venue_list"][0].name == "Venue 1"
        assert response.context["venue_list"][1].name == "Venue 2"

    def test_simple_table(self):
        """Create a simple, single day table with 3 slots and 2 venues and
           check we get the expected results"""
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue2 = Venue.objects.create(order=2, name='Venue 2')

        start1 = D.datetime(2013, 9, 22, 10, 0, 0, tzinfo=utc)
        start2 = D.datetime(2013, 9, 22, 11, 0, 0, tzinfo=utc)
        start3 = D.datetime(2013, 9, 22, 12, 0, 0, tzinfo=utc)
        end = D.datetime(2013, 9, 22, 13, 0, 0, tzinfo=utc)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2)
        slot2 = Slot.objects.create(start_time=start2, end_time=start3)
        slot3 = Slot.objects.create(start_time=start3, end_time=end)
        item1 = ScheduleItem.objects.create(venue=venue1, details="Item 1")
        item2 = ScheduleItem.objects.create(venue=venue1, details="Item 2")
        item3 = ScheduleItem.objects.create(venue=venue1, details="Item 3")
        item4 = ScheduleItem.objects.create(venue=venue2, details="Item 4")
        item5 = ScheduleItem.objects.create(venue=venue2, details="Item 5")
        item6 = ScheduleItem.objects.create(venue=venue2, details="Item 6")
        item1.slots.add(slot1)
        item4.slots.add(slot1)
        item2.slots.add(slot2)
        item5.slots.add(slot2)
        item3.slots.add(slot3)
        item6.slots.add(slot3)

        c = Client()
        response = c.get('/schedule/')

        days = response.context['table_days']

        assert start1.date() in days
        assert len(days[start1.date()]) == 3
        assert days[start1.date()][0].slot.start_time == start1
        assert days[start1.date()][0].slot.end_time == start2
        assert days[start1.date()][1].slot.start_time == start2
        assert days[start1.date()][1].slot.end_time == start3
        assert days[start1.date()][2].slot.start_time == start3
        assert days[start1.date()][2].slot.end_time == end

        assert len(days[start1.date()][0].items) == 2
        assert len(days[start1.date()][1].items) == 2
        assert len(days[start1.date()][2].items) == 2

        assert days[start1.date()][0].items[0]['item'] == item1
        assert days[start1.date()][0].items[0]['rowspan'] == 1
        assert days[start1.date()][0].items[0]['colspan'] == 1

        assert days[start1.date()][0].items[1]['item'] == item4
        assert days[start1.date()][0].items[1]['rowspan'] == 1
        assert days[start1.date()][0].items[1]['colspan'] == 1

        assert days[start1.date()][1].items[0]['item'] == item2
        assert days[start1.date()][1].items[0]['rowspan'] == 1
        assert days[start1.date()][1].items[0]['colspan'] == 1

        assert days[start1.date()][2].items[1]['item'] == item6
        assert days[start1.date()][2].items[1]['rowspan'] == 1
        assert days[start1.date()][2].items[1]['colspan'] == 1

    def test_multiple_days(self):
        """Create a multiple day table with 3 slots and 2 venues and
           check we get the expected results"""
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue2 = Venue.objects.create(order=2, name='Venue 2')

        start1 = D.datetime(2013, 9, 22, 10, 0, 0, tzinfo=utc)
        start2 = D.datetime(2013, 9, 22, 11, 0, 0, tzinfo=utc)
        end1 = D.datetime(2013, 9, 22, 12, 0, 0, tzinfo=utc)

        start3 = D.datetime(2013, 9, 23, 12, 0, 0, tzinfo=utc)
        end2 = D.datetime(2013, 9, 23, 13, 0, 0, tzinfo=utc)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2)
        slot2 = Slot.objects.create(start_time=start2, end_time=end1)
        slot3 = Slot.objects.create(start_time=start3, end_time=end2)
        item1 = ScheduleItem.objects.create(venue=venue1, details="Item 1")
        item2 = ScheduleItem.objects.create(venue=venue1, details="Item 2")
        item3 = ScheduleItem.objects.create(venue=venue1, details="Item 3")
        item4 = ScheduleItem.objects.create(venue=venue2, details="Item 4")
        item5 = ScheduleItem.objects.create(venue=venue2, details="Item 5")
        item6 = ScheduleItem.objects.create(venue=venue2, details="Item 6")
        item1.slots.add(slot1)
        item4.slots.add(slot1)
        item2.slots.add(slot2)
        item5.slots.add(slot2)
        item3.slots.add(slot3)
        item6.slots.add(slot3)

        c = Client()
        response = c.get('/schedule/')

        days = response.context['table_days']

        assert start1.date() in days
        assert start3.date() in days
        assert len(days[start1.date()]) == 2
        assert len(days[start3.date()]) == 1
        assert days[start1.date()][0].slot.start_time == start1
        assert days[start1.date()][0].slot.end_time == start2
        assert days[start1.date()][1].slot.start_time == start2
        assert days[start1.date()][1].slot.end_time == end1
        assert days[start3.date()][0].slot.start_time == start3
        assert days[start3.date()][0].slot.end_time == end2

        assert len(days[start1.date()][0].items) == 2
        assert len(days[start1.date()][1].items) == 2
        assert len(days[start3.date()][0].items) == 2

        assert days[start1.date()][0].items[0]['item'] == item1
        assert days[start1.date()][0].items[0]['rowspan'] == 1
        assert days[start1.date()][0].items[0]['colspan'] == 1

        assert days[start3.date()][0].items[1]['item'] == item6
        assert days[start3.date()][0].items[1]['rowspan'] == 1
        assert days[start3.date()][0].items[1]['colspan'] == 1
