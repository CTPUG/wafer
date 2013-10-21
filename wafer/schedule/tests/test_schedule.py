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
        slot2 = Slot.objects.create(previous_slot=slot1, end_time=start3)
        slot3 = Slot.objects.create(previous_slot=slot2, end_time=end)
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

        thedate = start1.date()

        assert thedate in days
        assert len(days[thedate]) == 3
        assert days[thedate][0].slot.get_start_time() == start1
        assert days[thedate][0].slot.end_time == start2
        assert days[thedate][1].slot.get_start_time() == start2
        assert days[thedate][1].slot.end_time == start3
        assert days[thedate][2].slot.get_start_time() == start3
        assert days[thedate][2].slot.end_time == end

        assert len(days[thedate][0].items) == 2
        assert len(days[thedate][1].items) == 2
        assert len(days[thedate][2].items) == 2

        assert days[thedate][0].get_sorted_items()[0]['item'] == item1
        assert days[thedate][0].get_sorted_items()[0]['rowspan'] == 1
        assert days[thedate][0].get_sorted_items()[0]['colspan'] == 1

        assert days[thedate][0].get_sorted_items()[1]['item'] == item4
        assert days[thedate][0].get_sorted_items()[1]['rowspan'] == 1
        assert days[thedate][0].get_sorted_items()[1]['colspan'] == 1

        assert days[thedate][1].get_sorted_items()[0]['item'] == item2
        assert days[thedate][1].get_sorted_items()[0]['rowspan'] == 1
        assert days[thedate][1].get_sorted_items()[0]['colspan'] == 1

        assert days[thedate][2].get_sorted_items()[1]['item'] == item6
        assert days[thedate][2].get_sorted_items()[1]['rowspan'] == 1
        assert days[thedate][2].get_sorted_items()[1]['colspan'] == 1

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

        date1 = start1.date()
        date2 = start3.date()

        assert date1 in days
        assert date2 in days
        assert len(days[date1]) == 2
        assert len(days[date2]) == 1
        assert days[date1][0].slot.get_start_time() == start1
        assert days[date1][0].slot.end_time == start2
        assert days[date1][1].slot.get_start_time() == start2
        assert days[date1][1].slot.end_time == end1
        assert days[date2][0].slot.get_start_time() == start3
        assert days[date2][0].slot.end_time == end2

        assert len(days[date1][0].items) == 2
        assert len(days[date1][1].items) == 2
        assert len(days[date2][0].items) == 2

        assert days[date1][0].get_sorted_items()[0]['item'] == item1
        assert days[date1][0].get_sorted_items()[0]['rowspan'] == 1
        assert days[date1][0].get_sorted_items()[0]['colspan'] == 1

        assert days[date2][0].get_sorted_items()[1]['item'] == item6
        assert days[date2][0].get_sorted_items()[1]['rowspan'] == 1
        assert days[date2][0].get_sorted_items()[1]['colspan'] == 1

    def test_col_span(self):
        """Create table with 3 venues and some interesting 
           venue spanning items"""
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue3 = Venue.objects.create(order=3, name='Venue 3')

        start1 = D.datetime(2013, 9, 22, 10, 0, 0, tzinfo=utc)
        start2 = D.datetime(2013, 9, 22, 11, 0, 0, tzinfo=utc)
        start3 = D.datetime(2013, 9, 22, 12, 0, 0, tzinfo=utc)
        start4 = D.datetime(2013, 9, 22, 13, 0, 0, tzinfo=utc)
        start5 = D.datetime(2013, 9, 22, 14, 0, 0, tzinfo=utc)
        end = D.datetime(2013, 9, 23, 15, 0, 0, tzinfo=utc)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2)
        slot2 = Slot.objects.create(start_time=start2, end_time=start3)
        slot3 = Slot.objects.create(start_time=start3, end_time=start4)
        slot4 = Slot.objects.create(start_time=start4, end_time=start5)
        slot5 = Slot.objects.create(start_time=start5, end_time=end)

        item1 = ScheduleItem.objects.create(venue=venue1, details="Item 1")
        item2 = ScheduleItem.objects.create(venue=venue1, details="Item 2")
        item3 = ScheduleItem.objects.create(venue=venue2, details="Item 3")
        item4 = ScheduleItem.objects.create(venue=venue3, details="Item 4")
        item5 = ScheduleItem.objects.create(venue=venue3, details="Item 5")
        item6 = ScheduleItem.objects.create(venue=venue3, details="Item 6")
        item7 = ScheduleItem.objects.create(venue=venue2, details="Item 7")
        item8 = ScheduleItem.objects.create(venue=venue1, details="Item 8")
        item9 = ScheduleItem.objects.create(venue=venue2, details="Item 9")
        item10 = ScheduleItem.objects.create(venue=venue3, details="Item 10")

        item1.slots.add(slot1)
        item5.slots.add(slot1)
        item2.slots.add(slot2)
        item3.slots.add(slot2)
        item4.slots.add(slot2)
        item6.slots.add(slot3)
        item7.slots.add(slot3)
        item8.slots.add(slot4)
        item9.slots.add(slot5)
        item10.slots.add(slot5)

        c = Client()
        response = c.get('/schedule/')

        days = response.context['table_days']

        thedate = start1.date()

        assert thedate in days
        assert len(days[thedate]) == 5
        assert days[thedate][0].slot.get_start_time() == start1
        assert days[thedate][1].slot.get_start_time() == start2
        assert days[thedate][2].slot.get_start_time() == start3
        assert days[thedate][3].slot.get_start_time() == start4
        assert days[thedate][4].slot.get_start_time() == start5

        assert len(days[thedate][0].items) == 2
        assert len(days[thedate][1].items) == 3
        assert len(days[thedate][2].items) == 2
        assert len(days[thedate][3].items) == 1
        assert len(days[thedate][4].items) == 2

        assert days[thedate][0].get_sorted_items()[0]['item'] == item1
        assert days[thedate][0].get_sorted_items()[0]['rowspan'] == 1
        assert days[thedate][0].get_sorted_items()[0]['colspan'] == 2

        assert days[thedate][0].get_sorted_items()[1]['item'] == item5
        assert days[thedate][0].get_sorted_items()[1]['rowspan'] == 1
        assert days[thedate][0].get_sorted_items()[1]['colspan'] == 1

        assert days[thedate][1].get_sorted_items()[0]['item'] == item2
        assert days[thedate][1].get_sorted_items()[0]['rowspan'] == 1
        assert days[thedate][1].get_sorted_items()[0]['colspan'] == 1

        assert days[thedate][1].get_sorted_items()[1]['item'] == item3
        assert days[thedate][1].get_sorted_items()[1]['rowspan'] == 1
        assert days[thedate][1].get_sorted_items()[1]['colspan'] == 1

        assert days[thedate][1].get_sorted_items()[2]['item'] == item4
        assert days[thedate][1].get_sorted_items()[2]['rowspan'] == 1
        assert days[thedate][1].get_sorted_items()[2]['colspan'] == 1

        assert days[thedate][2].get_sorted_items()[0]['item'] == item7
        assert days[thedate][2].get_sorted_items()[0]['rowspan'] == 1
        assert days[thedate][2].get_sorted_items()[0]['colspan'] == 2

        assert days[thedate][2].get_sorted_items()[1]['item'] == item6
        assert days[thedate][2].get_sorted_items()[1]['rowspan'] == 1
        assert days[thedate][2].get_sorted_items()[1]['colspan'] == 1

        assert days[thedate][3].get_sorted_items()[0]['item'] == item8
        assert days[thedate][3].get_sorted_items()[0]['rowspan'] == 1
        assert days[thedate][3].get_sorted_items()[0]['colspan'] == 3

        assert days[thedate][4].get_sorted_items()[0]['item'] == item9
        assert days[thedate][4].get_sorted_items()[0]['rowspan'] == 1
        assert days[thedate][4].get_sorted_items()[0]['colspan'] == 2

        assert days[thedate][4].get_sorted_items()[1]['item'] == item10
        assert days[thedate][4].get_sorted_items()[1]['rowspan'] == 1
        assert days[thedate][4].get_sorted_items()[1]['colspan'] == 1

    def test_row_span(self):
        """Create a day table with multiple slot items"""
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue2 = Venue.objects.create(order=2, name='Venue 2')

        start1 = D.datetime(2013, 9, 22, 10, 0, 0, tzinfo=utc)
        start2 = D.datetime(2013, 9, 22, 11, 0, 0, tzinfo=utc)
        start3 = D.datetime(2013, 9, 22, 12, 0, 0, tzinfo=utc)
        start4 = D.datetime(2013, 9, 22, 13, 0, 0, tzinfo=utc)
        start5= D.datetime(2013, 9, 22, 14, 0, 0, tzinfo=utc)
        end = D.datetime(2013, 9, 22, 15, 0, 0, tzinfo=utc)


        slot1 = Slot.objects.create(start_time=start1, end_time=start2)
        slot2 = Slot.objects.create(start_time=start2, end_time=start3)
        slot3 = Slot.objects.create(start_time=start3, end_time=start4)
        slot4 = Slot.objects.create(start_time=start4, end_time=start5)
        slot5 = Slot.objects.create(start_time=start5, end_time=end)

        item1 = ScheduleItem.objects.create(venue=venue1, details="Item 1")
        item2 = ScheduleItem.objects.create(venue=venue1, details="Item 2")
        item3 = ScheduleItem.objects.create(venue=venue1, details="Item 3")
        item4 = ScheduleItem.objects.create(venue=venue1, details="Item 4")
        item5 = ScheduleItem.objects.create(venue=venue2, details="Item 5")
        item6 = ScheduleItem.objects.create(venue=venue2, details="Item 6")
        item7 = ScheduleItem.objects.create(venue=venue2, details="Item 7")
        item1.slots.add(slot1)
        item1.slots.add(slot2)
        item5.slots.add(slot1)
        item6.slots.add(slot2)
        item7.slots.add(slot3)
        item7.slots.add(slot4)
        item7.slots.add(slot5)
        item2.slots.add(slot3)
        item3.slots.add(slot4)
        item4.slots.add(slot5)

        c = Client()
        response = c.get('/schedule/')

        days = response.context['table_days']

        thedate = start1.date()

        assert thedate in days
        assert len(days[thedate]) == 5
        assert days[thedate][0].slot.get_start_time() == start1
        assert days[thedate][1].slot.get_start_time() == start2
        assert days[thedate][4].slot.end_time == end

        assert len(days[thedate][0].items) == 2
        assert len(days[thedate][1].items) == 1
        assert len(days[thedate][2].items) == 2
        assert len(days[thedate][3].items) == 1
        assert len(days[thedate][4].items) == 1

        assert days[thedate][0].get_sorted_items()[0]['item'] == item1
        assert days[thedate][0].get_sorted_items()[0]['rowspan'] == 2
        assert days[thedate][0].get_sorted_items()[0]['colspan'] == 1

        assert days[thedate][0].get_sorted_items()[1]['item'] == item5
        assert days[thedate][0].get_sorted_items()[1]['rowspan'] == 1
        assert days[thedate][0].get_sorted_items()[1]['colspan'] == 1

        assert days[thedate][1].get_sorted_items()[0]['item'] == item6
        assert days[thedate][1].get_sorted_items()[0]['rowspan'] == 1
        assert days[thedate][1].get_sorted_items()[0]['colspan'] == 1

        assert days[thedate][2].get_sorted_items()[0]['item'] == item2
        assert days[thedate][2].get_sorted_items()[0]['rowspan'] == 1
        assert days[thedate][2].get_sorted_items()[0]['colspan'] == 1

        assert days[thedate][2].get_sorted_items()[1]['item'] == item7
        assert days[thedate][2].get_sorted_items()[1]['rowspan'] == 3
        assert days[thedate][2].get_sorted_items()[1]['colspan'] == 1

        assert days[thedate][3].get_sorted_items()[0]['item'] == item3
        assert days[thedate][3].get_sorted_items()[0]['rowspan'] == 1
        assert days[thedate][3].get_sorted_items()[0]['colspan'] == 1

        assert days[thedate][4].get_sorted_items()[0]['item'] == item4
        assert days[thedate][4].get_sorted_items()[0]['rowspan'] == 1
        assert days[thedate][4].get_sorted_items()[0]['colspan'] == 1
