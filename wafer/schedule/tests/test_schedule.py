from django.test import Client, TestCase
from django.utils.timezone import utc
from django.contrib.auth.models import User

import datetime as D
from wafer.talks.models import Talk, ACCEPTED, REJECTED, PENDING
from wafer.pages.models import Page
from wafer.schedule.models import Venue, Slot, ScheduleItem
from wafer.schedule.admin import (validate_slots, validate_items,
                                  find_duplicate_schedule_items,
                                  find_clashes)


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

        # Schedule is
        #         Venue 1     Venue 2
        # 10-11   Item1       Item4
        # 11-12   Item2       Item5
        # 12-13   Item3       Item6
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

    def test_ordering(self):
        """Ensure we handle oddly ordered creation of items correctly"""
        # Schedule is
        #         Venue 1     Venue 2
        # 10-11   Item3       Item6
        # 11-12   Item2       Item5
        # 12-13   Item1       Item4
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
        item1.slots.add(slot3)
        item4.slots.add(slot3)
        item2.slots.add(slot2)
        item5.slots.add(slot2)
        item3.slots.add(slot1)
        item6.slots.add(slot1)

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

        assert days[thedate][0].get_sorted_items()[0]['item'] == item3
        assert days[thedate][0].get_sorted_items()[0]['rowspan'] == 1
        assert days[thedate][0].get_sorted_items()[0]['colspan'] == 1

        assert days[thedate][0].get_sorted_items()[1]['item'] == item6
        assert days[thedate][0].get_sorted_items()[1]['rowspan'] == 1
        assert days[thedate][0].get_sorted_items()[1]['colspan'] == 1

        assert days[thedate][1].get_sorted_items()[0]['item'] == item2
        assert days[thedate][1].get_sorted_items()[0]['rowspan'] == 1
        assert days[thedate][1].get_sorted_items()[0]['colspan'] == 1

        assert days[thedate][2].get_sorted_items()[1]['item'] == item4
        assert days[thedate][2].get_sorted_items()[1]['rowspan'] == 1
        assert days[thedate][2].get_sorted_items()[1]['colspan'] == 1


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
        # Schedule is
        #         Venue 1     Venue 2   Venue3
        # 10-11   Item1       --        Item5
        # 11-12   Item2       Item3     Item4
        # 12-13   --          Item7     Item6
        # 13-14   Item8       --        --
        # 14-15   --          Item9     Item10
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
        # Schedule is
        #         Venue 1     Venue 2
        # 10-11   Item1       Item5
        # 11-12     |         Item6
        # 12-13   Item2       Item7
        # 13-14   Item3         |
        # 14-15   Item4         |
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue2 = Venue.objects.create(order=2, name='Venue 2')

        start1 = D.datetime(2013, 9, 22, 10, 0, 0, tzinfo=utc)
        start2 = D.datetime(2013, 9, 22, 11, 0, 0, tzinfo=utc)
        start3 = D.datetime(2013, 9, 22, 12, 0, 0, tzinfo=utc)
        start4 = D.datetime(2013, 9, 22, 13, 0, 0, tzinfo=utc)
        start5 = D.datetime(2013, 9, 22, 14, 0, 0, tzinfo=utc)
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


class ValidationTests(TestCase):

    def test_slot(self):
        """Test detection of overlapping slots"""
        start1 = D.datetime(2013, 9, 22, 10, 0, 0, tzinfo=utc)
        start2 = D.datetime(2013, 9, 22, 11, 0, 0, tzinfo=utc)
        start3 = D.datetime(2013, 9, 22, 12, 0, 0, tzinfo=utc)
        start35 = D.datetime(2013, 9, 22, 12, 30, 0, tzinfo=utc)
        start4 = D.datetime(2013, 9, 22, 13, 0, 0, tzinfo=utc)
        start45 = D.datetime(2013, 9, 22, 13, 30, 0, tzinfo=utc)
        start5 = D.datetime(2013, 9, 22, 14, 0, 0, tzinfo=utc)
        end = D.datetime(2013, 9, 22, 15, 0, 0, tzinfo=utc)

        # Test common start time
        slot1 = Slot.objects.create(start_time=start1, end_time=start2)
        slot2 = Slot.objects.create(start_time=start1, end_time=end)

        overlaps = validate_slots()
        assert len(overlaps) == 2
        assert slot1 in overlaps
        assert slot2 in overlaps

        slot2.start_time = start5
        slot2.save()

        # Test interleaved slot
        slot3 = Slot.objects.create(start_time=start2, end_time=start3)
        slot4 = Slot.objects.create(start_time=start4, end_time=start5)
        slot5 = Slot.objects.create(start_time=start35, end_time=start45)

        overlaps = validate_slots()
        assert len(overlaps) == 2
        assert slot4 in overlaps
        assert slot5 in overlaps

        # Test no overlap
        slot5.start_time = start3
        slot5.end_time = start4
        slot5.save()
        overlaps = validate_slots()
        assert len(overlaps) == 0

        # Test common end time
        slot5.end_time = start5
        slot5.save()
        overlaps = validate_slots()
        assert len(overlaps) == 2
        assert slot4 in overlaps
        assert slot5 in overlaps

        # Test overlap detect with previous slot set
        slot5.start_time = None
        slot5.end_time = start5
        slot5.previous_slot = slot1
        slot5.save()
        overlaps = validate_slots()
        assert len(overlaps) == 3
        assert slot5 in overlaps
        assert slot3 in overlaps
        assert slot4 in overlaps

    def test_clashes(self):
        """Test that we can detect clashes correctly"""
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue2 = Venue.objects.create(order=2, name='Venue 2')

        start1 = D.datetime(2013, 9, 22, 10, 0, 0, tzinfo=utc)
        start2 = D.datetime(2013, 9, 22, 11, 0, 0, tzinfo=utc)
        end = D.datetime(2013, 9, 22, 12, 0, 0, tzinfo=utc)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2)
        slot2 = Slot.objects.create(start_time=start2, end_time=end)

        item1 = ScheduleItem.objects.create(venue=venue1, details="Item 1")
        item2 = ScheduleItem.objects.create(venue=venue1, details="Item 2")
        # Create a simple venue/slot clash
        item1.slots.add(slot1)
        item2.slots.add(slot1)
        clashes = find_clashes()
        assert len(clashes) == 1
        pos = (venue1, slot1)
        assert pos in clashes
        assert item1 in clashes[pos]
        assert item2 in clashes[pos]
        # Create a overlapping clashes
        item2.slots.remove(slot1)
        item1.slots.add(slot2)
        item2.slots.add(slot2)
        clashes = find_clashes()
        assert len(clashes) == 1
        pos = (venue1, slot2)
        assert pos in clashes
        assert item1 in clashes[pos]
        assert item2 in clashes[pos]
        # Add a clash in a second venue
        item3 = ScheduleItem.objects.create(venue=venue2, details="Item 3")
        item4 = ScheduleItem.objects.create(venue=venue2, details="Item 4")
        item3.slots.add(slot2)
        item4.slots.add(slot2)
        clashes = find_clashes()
        assert len(clashes) == 2
        pos = (venue2, slot2)
        assert pos in clashes
        assert item3 in clashes[pos]
        assert item4 in clashes[pos]
        # Fix clashes
        item1.slots.remove(slot2)
        item3.slots.remove(slot2)
        item3.slots.add(slot1)
        clashes = find_clashes()
        assert len(clashes) == 0

    def test_validation(self):
        """Test that we detect validation errors correctly"""
        # Create a item with both a talk and a page assigned
        venue1 = Venue.objects.create(order=1, name='Venue 1')

        start1 = D.datetime(2013, 9, 22, 10, 0, 0, tzinfo=utc)
        start2 = D.datetime(2013, 9, 22, 11, 0, 0, tzinfo=utc)
        end = D.datetime(2013, 9, 22, 12, 0, 0, tzinfo=utc)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2)
        slot2 = Slot.objects.create(start_time=start1, end_time=end)

        user = User.objects.create_user('john', 'best@wafer.test',
                                        'johnpassword')
        talk = Talk.objects.create(title="Test talk", status=ACCEPTED,
                                   corresponding_author_id=user.id)
        page = Page.objects.create(name="test page", slug="test")

        item1 = ScheduleItem.objects.create(venue=venue1,
                                            talk_id=talk.pk,
                                            page_id=page.pk)
        item1.slots.add(slot1)

        invalid = validate_items()
        assert len(invalid) == 1
        assert item1 in invalid

        item2 = ScheduleItem.objects.create(venue=venue1,
                                            talk_id=talk.pk)
        item2.slots.add(slot2)

        # Test talk status
        talk.status = REJECTED
        talk.save()
        invalid = validate_items()
        assert len(invalid) == 2
        assert item2 in invalid

        talk.status = PENDING
        talk.save()
        invalid = validate_items()
        assert len(invalid) == 2
        assert item2 in invalid

        talk.status = ACCEPTED
        talk.save()
        invalid = validate_items()
        assert len(invalid) == 1
        assert item2 not in invalid

    def test_duplicates(self):
        """Test that we can detect duplicates talks and pages"""
        # Final chedule is
        #       Venue 1  Venue 2
        # 10-11 Talk 1   Page 1
        # 11-12 Talk 1   Page 1
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue2 = Venue.objects.create(order=2, name='Venue 2')

        start1 = D.datetime(2013, 9, 22, 10, 0, 0, tzinfo=utc)
        start2 = D.datetime(2013, 9, 22, 11, 0, 0, tzinfo=utc)
        end = D.datetime(2013, 9, 22, 12, 0, 0, tzinfo=utc)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2)
        slot2 = Slot.objects.create(start_time=start1, end_time=end)

        user = User.objects.create_user('john', 'best@wafer.test',
                                        'johnpassword')
        talk = Talk.objects.create(title="Test talk", status=ACCEPTED,
                                   corresponding_author_id=user.id)
        page1 = Page.objects.create(name="test page", slug="test")
        page2 = Page.objects.create(name="test page 2", slug="test2")

        item1 = ScheduleItem.objects.create(venue=venue1,
                                            talk_id=talk.pk)
        item1.slots.add(slot1)
        item2 = ScheduleItem.objects.create(venue=venue1,
                                            talk_id=talk.pk)
        item2.slots.add(slot2)

        duplicates = find_duplicate_schedule_items()
        assert len(duplicates) == 2
        assert item1 in duplicates
        assert item2 in duplicates

        item3 = ScheduleItem.objects.create(venue=venue2,
                                            page_id=page1.pk)
        item3.slots.add(slot1)
        item4 = ScheduleItem.objects.create(venue=venue2,
                                            page_id=page1.pk)
        item4.slots.add(slot2)

        duplicates = find_duplicate_schedule_items()
        assert len(duplicates) == 4
        assert item3 in duplicates
        assert item4 in duplicates

        item4.page_id = page2.pk
        item4.save()

        duplicates = find_duplicate_schedule_items()
        assert len(duplicates) == 2
        assert item3 not in duplicates
        assert item4 not in duplicates
