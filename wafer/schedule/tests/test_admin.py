import datetime as D

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.http import HttpRequest

from wafer.pages.models import Page
from wafer.schedule.admin import (
    SlotAdmin, SlotDayFilter, ScheduleItemDayFilter, SlotStartTimeFilter,
    ScheduleItemStartTimeFilter, ScheduleItemVenueFilter,
    prefetch_schedule_items, prefetch_slots,
    find_overlapping_slots, validate_items,
    find_duplicate_schedule_items, find_clashes, find_invalid_venues,
    find_non_contiguous,
    check_schedule, validate_schedule)
from wafer.schedule.models import Day, Venue, Slot, ScheduleItem
from wafer.talks.models import (Talk, ACCEPTED, REJECTED, CANCELLED,
                                SUBMITTED, UNDER_CONSIDERATION)


class DummyForm(object):

    def __init__(self):
        self.cleaned_data = {}


def make_dummy_form(additional):
    """Fake a form object for the tests"""
    form = DummyForm()
    form.cleaned_data['additional'] = additional
    return form


class SlotAdminTests(TestCase):

    def setUp(self):
        """Create some Venues and Days for use in the actual tests."""
        self.day = Day.objects.create(date=D.date(2013, 9, 22))
        self.admin = SlotAdmin(Slot, None)

    def test_save_model_single_new(self):
        """Test save_model creating a new slot, but no additional slots"""
        slot = Slot(day=self.day, start_time=D.time(11, 0, 0),
                    end_time=D.time(11, 30, 0))
        # check that it's not saved in the database yet
        self.assertEqual(Slot.objects.count(), 0)
        request = HttpRequest()
        dummy = make_dummy_form(0)
        self.admin.save_model(request, slot, dummy, False)
        # check that it's now been saved in the database
        self.assertEqual(Slot.objects.count(), 1)
        slot2 = Slot.objects.filter(start_time=D.time(11, 0, 0)).get()
        self.assertEqual(slot, slot2)

    def test_save_model_change_slot(self):
        """Test save_model changing a slot"""
        slot = Slot(day=self.day, start_time=D.time(11, 0, 0),
                    end_time=D.time(12, 30, 0))
        # end_time is chosen as 12:30 so it stays valid through all the
        # subsequent fiddling
        slot.save()
        # check that it's saved in the database
        self.assertEqual(Slot.objects.count(), 1)
        request = HttpRequest()
        dummy = make_dummy_form(0)
        slot.start_time = D.time(12, 0, 0)
        self.assertEqual(
            Slot.objects.filter(start_time=D.time(11, 0, 0)).count(), 1)
        self.admin.save_model(request, slot, dummy, True)
        # Check that the database has changed
        self.assertEqual(
            Slot.objects.filter(start_time=D.time(11, 0, 0)).count(), 0)
        self.assertEqual(Slot.objects.count(), 1)
        slot2 = Slot.objects.filter(start_time=D.time(12, 0, 0)).get()
        self.assertEqual(slot, slot2)

        # Check that setting additional has no influence on the change path
        dummy = make_dummy_form(3)
        slot.start_time = D.time(11, 0, 0)
        self.assertEqual(
            Slot.objects.filter(start_time=D.time(11, 0, 0)).count(), 0)
        self.admin.save_model(request, slot, dummy, True)
        # Still only 1 object
        self.assertEqual(Slot.objects.count(), 1)
        # And it has been updated
        self.assertEqual(
            Slot.objects.filter(start_time=D.time(12, 0, 0)).count(), 0)
        self.assertEqual(
            Slot.objects.filter(start_time=D.time(11, 0, 0)).count(), 1)

    def test_save_model_new_additional(self):
        """Test save_model changing a new slot with some additional slots"""
        slot = Slot(day=self.day, start_time=D.time(11, 0, 0),
                    end_time=D.time(11, 30, 0))
        # check that it's not saved in the database
        self.assertEqual(Slot.objects.count(), 0)
        request = HttpRequest()
        dummy = make_dummy_form(3)
        self.admin.save_model(request, slot, dummy, False)
        self.assertEqual(Slot.objects.count(), 4)

        # check the hierachy is created correctly
        slot1 = Slot.objects.filter(previous_slot=slot).get()
        self.assertEqual(slot1.get_start_time(), slot.end_time)
        self.assertEqual(slot1.end_time, D.time(12, 0, 0))
        slot2 = Slot.objects.filter(previous_slot=slot1).get()
        self.assertEqual(slot2.get_start_time(), slot1.end_time)
        self.assertEqual(slot2.end_time, D.time(12, 30, 0))
        self.assertEqual(slot2.day, slot.day)
        slot3 = Slot.objects.filter(previous_slot=slot2).get()
        self.assertEqual(slot3.get_start_time(), slot2.end_time)
        self.assertEqual(slot3.end_time, D.time(13, 00, 0))
        self.assertEqual(slot3.day, slot.day)

        # repeat checks with a different length of slot
        slot = Slot(day=self.day, previous_slot=slot3,
                    end_time=D.time(14, 30, 0))
        dummy = make_dummy_form(4)
        self.admin.save_model(request, slot, dummy, False)
        self.assertEqual(Slot.objects.count(), 9)
        slot1 = Slot.objects.filter(previous_slot=slot).get()
        self.assertEqual(slot1.get_start_time(), slot.end_time)
        self.assertEqual(slot1.end_time, D.time(16, 0, 0))
        slot2 = Slot.objects.filter(previous_slot=slot1).get()
        self.assertEqual(slot2.get_start_time(), slot1.end_time)
        self.assertEqual(slot2.end_time, D.time(17, 30, 0))
        self.assertEqual(slot2.day, slot.day)
        slot3 = Slot.objects.filter(previous_slot=slot2).get()
        self.assertEqual(slot3.get_start_time(), slot2.end_time)
        self.assertEqual(slot3.end_time, D.time(19, 00, 0))
        self.assertEqual(slot3.day, slot.day)
        slot4 = Slot.objects.filter(previous_slot=slot3).get()
        self.assertEqual(slot4.get_start_time(), slot3.end_time)
        self.assertEqual(slot4.end_time, D.time(20, 30, 0))
        self.assertEqual(slot4.day, slot.day)

    def test_save_model_prev_slot_additional(self):
        """Test save_model changing a new slot with some additional slots,
           starting from a slot specified via previous slot"""
        prev_slot = Slot(day=self.day, start_time=D.time(11, 0, 0),
                         end_time=D.time(11, 30, 0))
        prev_slot.save()
        self.assertEqual(Slot.objects.count(), 1)
        slot = Slot(previous_slot=prev_slot, end_time=D.time(12, 00, 0))
        # Check that newly added slot isn't in the database
        self.assertEqual(Slot.objects.count(), 1)
        request = HttpRequest()
        dummy = make_dummy_form(2)
        self.admin.save_model(request, slot, dummy, False)
        self.assertEqual(Slot.objects.count(), 4)

        # check the hierachy is created correctly
        slot1 = Slot.objects.filter(previous_slot=slot).get()
        self.assertEqual(slot1.get_start_time(), slot.end_time)
        self.assertEqual(slot1.end_time, D.time(12, 30, 0))
        slot2 = Slot.objects.filter(previous_slot=slot1).get()
        self.assertEqual(slot2.get_start_time(), slot1.end_time)
        self.assertEqual(slot2.end_time, D.time(13, 00, 0))


class SlotListFilterTest(TestCase):
    """Test the list filter"""
    # Because of how we implement the filter, the order of results
    # won't match order of creation or time order. This isn't
    # serious, because the admin interface will sort things
    # anyway by the user's chosen key, but it does mean we use sets
    # in several test case to avoid issues with this.

    def setUp(self):
        """Create some data for use in the actual tests."""
        self.day1 = Day.objects.create(date=D.date(2013, 9, 22))
        self.day2 = Day.objects.create(date=D.date(2013, 9, 23))
        self.day3 = Day.objects.create(date=D.date(2013, 9, 24))

        self.admin = SlotAdmin(Slot, None)

    def _make_day_filter(self, day):
        """create a list filter for testing."""
        # We can get away with request None, since SimpleListFilter
        # doesn't use request in the bits we want to test
        if day:
            return SlotDayFilter(None, {'day': str(day.pk)}, Slot, self.admin)
        else:
            return SlotDayFilter(None, {'day': None}, Slot, self.admin)

    def _make_time_filter(self, time):
        """create a list filter for testing."""
        if time:
            return SlotStartTimeFilter(None, {'start': time}, Slot, self.admin)
        else:
            return SlotStarTimeFilter(None, {'start': None}, Slot, self.admin)

    def test_day_filter_lookups(self):
        """Test that filter lookups are sane."""
        TestFilter = self._make_day_filter(self.day1)
        # Check lookup details
        lookups = TestFilter.lookups(None, self.admin)
        self.assertEqual(len(lookups), 3)
        self.assertEqual(lookups[0], ('%d' % self.day1.pk, str(self.day1)))
        TestFilter = self._make_day_filter(self.day3)
        lookups2 = TestFilter.lookups(None, self.admin)
        self.assertEqual(lookups, lookups2)

    def test_time_filter_lookups(self):
        """Test that filter lookups are sane."""
        # Add some slots
        slot1 = Slot(day=self.day1, start_time=D.time(11, 0, 0),
                    end_time=D.time(12, 00, 0))
        slot2 = Slot(day=self.day2, start_time=D.time(11, 0, 0),
                    end_time=D.time(12, 00, 0))
        slot3 = Slot(day=self.day1, start_time=D.time(12, 0, 0),
                      end_time=D.time(13, 0, 0))
        slot4 = Slot(day=self.day1, start_time=D.time(13, 0, 0),
                      end_time=D.time(14, 0, 0))
        slot1.save()
        slot2.save()
        slot3.save()
        slot4.save()
        TestFilter = self._make_time_filter('11:00')
        # Check lookup details
        lookups = list(TestFilter.lookups(None, self.admin))
        self.assertEqual(len(lookups), 3)
        self.assertEqual(lookups[0], ('11:00', '11:00'))
        TestFilter = self._make_time_filter('12:00')
        lookups2 = list(TestFilter.lookups(None, self.admin))
        self.assertEqual(lookups, lookups2)

    def test_queryset_day_time(self):
        """Test queries with slots created purely by day + start_time"""
        slots = {}
        slots[self.day1] = [Slot(day=self.day1, start_time=D.time(11, 0, 0),
                    end_time=D.time(12, 00, 0))]
        slots[self.day2] = [Slot(day=self.day2, start_time=D.time(11, 0, 0),
                    end_time=D.time(12, 00, 0))]

        # Day1 slots
        for x in range(12, 17):
            slots[self.day1].append(Slot(day=self.day1,
                                         start_time=D.time(x, 0, 0),
                                         end_time=D.time(x+1, 0, 0)))
            if x < 15:
                # Fewer slots for day 2
                slots[self.day2].append(Slot(day=self.day2,
                                             start_time=D.time(x, 0, 0),
                                             end_time=D.time(x+1, 0, 0)))
        for d in slots:
            for s in slots[d]:
                s.save()
        # Check Null filter
        TestFilter = self._make_day_filter(None)
        self.assertEqual(list(TestFilter.queryset(None, Slot.objects.all())),
                         list(Slot.objects.all()))
        # Test Day1
        TestFilter = self._make_day_filter(self.day1)
        queries = set(TestFilter.queryset(None, Slot.objects.all()))
        self.assertEqual(queries, set(slots[self.day1]))
        # Test Day2
        TestFilter = self._make_day_filter(self.day2)
        queries = set(TestFilter.queryset(None, Slot.objects.all()))
        self.assertEqual(queries, set(slots[self.day2]))

        # Check no match case
        TestFilter = self._make_day_filter(self.day3)
        queries = list(TestFilter.queryset(None, Slot.objects.all()))
        self.assertEqual(queries, [])

        # Check for slots starting at 11:00
        TestFilter = self._make_time_filter('11:00')
        # Should be the first slot of each day
        queries = set(TestFilter.queryset(None, Slot.objects.all()))
        self.assertEqual(queries,
                         set([slots[self.day1][0], slots[self.day2][0]]))

        TestFilter = self._make_time_filter('12:00')
        # Should be the second slot of each day
        queries = set(TestFilter.queryset(None, Slot.objects.all()))
        self.assertEqual(queries,
                         set([slots[self.day1][1], slots[self.day2][1]]))

    def test_queryset_prev_slot(self):
        """Test lookup with a chain of previous slots."""
        slots = {}
        prev = Slot(day=self.day1, start_time=D.time(11, 0, 0),
                    end_time=D.time(12, 00, 0))
        prev.save()
        slots[self.day1] = [prev]
        prev = Slot(day=self.day2, start_time=D.time(11, 0, 0),
                    end_time=D.time(12, 00, 0))
        prev.save()
        slots[self.day2] = [prev]
        # Day1 slots
        for x in range(12, 17):
            prev1 = slots[self.day1][-1]
            slots[self.day1].append(Slot(previous_slot=prev1,
                                         end_time=D.time(x+1, 0, 0)))
            slots[self.day1][-1].save()
            if x < 15:
                prev2 = slots[self.day2][-1]
                # Fewer slots for day 2
                slots[self.day2].append(Slot(previous_slot=prev2,
                                             end_time=D.time(x+1, 0, 0)))
                slots[self.day2][-1].save()
        # Check Null filter
        TestFilter = self._make_day_filter(None)
        self.assertEqual(list(TestFilter.queryset(None, Slot.objects.all())),
                         list(Slot.objects.all()))
        # Test Day1
        TestFilter = self._make_day_filter(self.day1)
        queries = set(TestFilter.queryset(None, Slot.objects.all()))
        self.assertEqual(queries, set(slots[self.day1]))
        # Test Day2
        TestFilter = self._make_day_filter(self.day2)
        queries = set(TestFilter.queryset(None, Slot.objects.all()))
        self.assertEqual(queries, set(slots[self.day2]))

        # Check no match case
        TestFilter = self._make_day_filter(self.day3)
        queries = list(TestFilter.queryset(None, Slot.objects.all()))
        self.assertEqual(queries, [])

        # Check for slots starting at 11:00
        TestFilter = self._make_time_filter('11:00')
        # Should be the first slot of each day
        queries = set(TestFilter.queryset(None, Slot.objects.all()))
        self.assertEqual(queries,
                         set([slots[self.day1][0], slots[self.day2][0]]))

        TestFilter = self._make_time_filter('12:00')
        # Should be the second slot of each day
        queries = set(TestFilter.queryset(None, Slot.objects.all()))
        self.assertEqual(queries,
                         set([slots[self.day1][1], slots[self.day2][1]]))

    def test_queryset_mixed(self):
        """Test with a mix of day+time and previous slot cases."""
        slots = {}
        prev = Slot(day=self.day1, start_time=D.time(11, 0, 0),
                    end_time=D.time(12, 00, 0))
        prev.save()
        slots[self.day1] = [prev]
        prev = Slot(day=self.day2, start_time=D.time(11, 0, 0),
                    end_time=D.time(12, 00, 0))
        prev.save()
        slots[self.day2] = [prev]
        # Day1 slots
        for x in range(12, 20):
            prev1 = slots[self.day1][-1]
            if x % 2:
                slots[self.day1].append(Slot(previous_slot=prev1,
                                             end_time=D.time(x+1, 0, 0)))
            else:
                slots[self.day1].append(Slot(day=self.day1,
                                             start_time=D.time(x, 0, 0),
                                             end_time=D.time(x+1, 0, 0)))

            slots[self.day1][-1].save()
            prev2 = slots[self.day2][-1]
            if x % 5:
                slots[self.day2].append(Slot(previous_slot=prev2,
                                             end_time=D.time(x+1, 0, 0)))
            else:
                slots[self.day2].append(Slot(day=self.day2,
                                             start_time=D.time(x, 0, 0),
                                             end_time=D.time(x+1, 0, 0)))
            slots[self.day2][-1].save()
        # Check Null filter
        TestFilter = self._make_day_filter(None)
        self.assertEqual(list(TestFilter.queryset(None, Slot.objects.all())),
                         list(Slot.objects.all()))
        # Test Day1
        TestFilter = self._make_day_filter(self.day1)
        queries = set(TestFilter.queryset(None, Slot.objects.all()))
        self.assertEqual(queries, set(slots[self.day1]))
        # Test Day2
        TestFilter = self._make_day_filter(self.day2)
        queries = set(TestFilter.queryset(None, Slot.objects.all()))
        self.assertEqual(queries, set(slots[self.day2]))

        # Check no match case
        TestFilter = self._make_day_filter(self.day3)
        queries = list(TestFilter.queryset(None, Slot.objects.all()))
        self.assertEqual(queries, [])


class ValidationTests(TestCase):

    def test_slot(self):
        """Test detection of overlapping slots"""
        day1 = Day.objects.create(date=D.date(2013, 9, 22))
        start1 = D.time(10, 0, 0)
        start2 = D.time(11, 0, 0)
        start3 = D.time(12, 0, 0)
        start35 = D.time(12, 30, 0)
        start4 = D.time(13, 0, 0)
        start45 = D.time(13, 30, 0)
        start5 = D.time(14, 0, 0)
        end = D.time(15, 0, 0)

        # Test common start time
        slot1 = Slot.objects.create(start_time=start1, end_time=start2,
                                    day=day1)
        slot2 = Slot.objects.create(start_time=start1, end_time=end, day=day1)

        all_slots = prefetch_slots()
        overlaps = find_overlapping_slots(all_slots)
        assert overlaps == set([slot1, slot2])

        slot2.start_time = start5
        slot2.save()

        # Test interleaved slot
        slot3 = Slot.objects.create(start_time=start2, end_time=start3,
                                    day=day1)
        slot4 = Slot.objects.create(start_time=start4, end_time=start5,
                                    day=day1)
        slot5 = Slot.objects.create(start_time=start35, end_time=start45,
                                    day=day1)

        all_slots = prefetch_slots()
        overlaps = find_overlapping_slots(all_slots)
        assert overlaps == set([slot4, slot5])

        # Test no overlap
        slot5.start_time = start3
        slot5.end_time = start4
        slot5.save()
        all_slots = prefetch_slots()
        overlaps = find_overlapping_slots(all_slots)
        assert len(overlaps) == 0

        # Test common end time
        slot5.end_time = start5
        slot5.save()
        all_slots = prefetch_slots()
        overlaps = find_overlapping_slots(all_slots)
        assert overlaps == set([slot4, slot5])

        # Test overlap detect with previous slot set
        slot5.start_time = None
        slot5.end_time = start5
        slot5.previous_slot = slot1
        slot5.save()
        all_slots = prefetch_slots()
        overlaps = find_overlapping_slots(all_slots)
        assert overlaps == set([slot3, slot4, slot5])

    def test_clashes(self):
        """Test that we can detect clashes correctly"""
        day1 = Day.objects.create(date=D.date(2013, 9, 22))
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue1.days.add(day1)
        venue2.days.add(day1)

        start1 = D.time(10, 0, 0)
        start2 = D.time(11, 0, 0)
        end = D.time(12, 0, 0)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2,
                                    day=day1)
        slot2 = Slot.objects.create(start_time=start2, end_time=end,
                                    day=day1)

        item1 = ScheduleItem.objects.create(venue=venue1, details="Item 1")
        item2 = ScheduleItem.objects.create(venue=venue1, details="Item 2")
        # Create a simple venue/slot clash
        item1.slots.add(slot1)
        item2.slots.add(slot1)
        all_items = prefetch_schedule_items()
        # Needs to be an explicit list, not a generator on python 3 here
        clashes = list(find_clashes(all_items))
        assert len(clashes) == 1
        pos = (venue1, slot1)
        assert pos == clashes[0][0]
        assert item1 in clashes[0][1]
        assert item2 in clashes[0][1]
        # Create a overlapping clashes
        item2.slots.remove(slot1)
        item1.slots.add(slot2)
        item2.slots.add(slot2)
        all_items = prefetch_schedule_items()
        clashes = list(find_clashes(all_items))
        assert len(clashes) == 1
        pos = (venue1, slot2)
        assert pos == clashes[0][0]
        assert item1 in clashes[0][1]
        assert item2 in clashes[0][1]
        # Add a clash in a second venue
        item3 = ScheduleItem.objects.create(venue=venue2, details="Item 3")
        item4 = ScheduleItem.objects.create(venue=venue2, details="Item 4")
        item3.slots.add(slot2)
        item4.slots.add(slot2)
        all_items = prefetch_schedule_items()
        clashes = list(find_clashes(all_items))
        assert len(clashes) == 2
        pos = (venue2, slot2)
        assert pos in [x[0] for x in clashes]
        clash_items = []
        for sublist in clashes:
            if sublist[0] == pos:
                clash_items.extend(sublist[1])
        assert item3 in clash_items
        assert item4 in clash_items
        # Fix clashes
        item1.slots.remove(slot2)
        item3.slots.remove(slot2)
        item3.slots.add(slot1)
        all_items = prefetch_schedule_items()
        clashes = find_clashes(all_items)
        assert len(clashes) == 0

    def test_validation(self):
        """Test that we detect validation errors correctly"""
        # Create a item with both a talk and a page assigned
        day1 = Day.objects.create(date=D.date(2013, 9, 22))
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue1.days.add(day1)

        start1 = D.time(10, 0, 0)
        start2 = D.time(11, 0, 0)
        end = D.time(12, 0, 0)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2,
                                    day=day1)
        slot2 = Slot.objects.create(start_time=start1, end_time=end,
                                    day=day1)

        user = get_user_model().objects.create_user('john', 'best@wafer.test',
                                                    'johnpassword')
        talk = Talk.objects.create(title="Test talk", status=ACCEPTED,
                                   corresponding_author_id=user.id)
        page = Page.objects.create(name="test page", slug="test")

        item1 = ScheduleItem.objects.create(venue=venue1,
                                            talk_id=talk.pk,
                                            page_id=page.pk)
        item1.slots.add(slot1)

        all_items = prefetch_schedule_items()
        invalid = validate_items(all_items)
        assert set(invalid) == set([item1])

        item2 = ScheduleItem.objects.create(venue=venue1,
                                            talk_id=talk.pk)
        item2.slots.add(slot2)

        # Test talk status
        talk.status = REJECTED
        talk.save()
        all_items = prefetch_schedule_items()
        invalid = validate_items(all_items)
        assert set(invalid) == set([item1, item2])

        talk.status = SUBMITTED
        talk.save()
        all_items = prefetch_schedule_items()
        invalid = validate_items(all_items)
        assert set(invalid) == set([item1, item2])

        talk.status = CANCELLED
        talk.save()
        all_items = prefetch_schedule_items()
        invalid = validate_items(all_items)
        assert set(invalid) == set([item1])

        talk.status = UNDER_CONSIDERATION
        talk.save()
        all_items = prefetch_schedule_items()
        invalid = validate_items(all_items)
        assert set(invalid) == set([item1, item2])

        talk.status = ACCEPTED
        talk.save()
        all_items = prefetch_schedule_items()
        invalid = validate_items(all_items)
        assert set(invalid) == set([item1])

        item3 = ScheduleItem.objects.create(venue=venue1,
                                            talk_id=None, page_id=None)
        item3.slots.add(slot2)

        all_items = prefetch_schedule_items()
        invalid = validate_items(all_items)
        assert set(invalid) == set([item1, item3])

    def test_non_contiguous(self):
        """Test that we detect items with non contiguous slots"""
        # Create a item with a gap in the slots assigned to it
        day1 = Day.objects.create(date=D.date(2013, 9, 22))
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue1.days.add(day1)

        start1 = D.time(10, 0, 0)
        start2 = D.time(11, 0, 0)
        start3 = D.time(12, 0, 0)
        end = D.time(13, 0, 0)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2,
                                    day=day1)
        slot2 = Slot.objects.create(start_time=start2, end_time=start3,
                                    day=day1)
        slot3 = Slot.objects.create(start_time=start3, end_time=end,
                                    day=day1)

        user = get_user_model().objects.create_user('john', 'best@wafer.test',
                                                    'johnpassword')
        talk = Talk.objects.create(title="Test talk", status=ACCEPTED,
                                   corresponding_author_id=user.id)
        page = Page.objects.create(name="test page", slug="test")

        item1 = ScheduleItem.objects.create(venue=venue1,
                                            talk_id=talk.pk)
        item1.slots.add(slot1)
        item1.slots.add(slot3)

        item2 = ScheduleItem.objects.create(venue=venue1,
                                            page_id=page.pk)
        item2.slots.add(slot2)

        all_items = prefetch_schedule_items()
        invalid = find_non_contiguous(all_items)
        # Only item1 is invalid
        assert set(invalid) == set([item1])

        item1.slots.add(slot2)
        item1.slots.remove(slot1)
        item2.slots.add(slot1)
        item2.slots.remove(slot2)

        all_items = prefetch_schedule_items()
        invalid = validate_items(all_items)
        # Everything is valid now
        assert set(invalid) == set([])

    def test_duplicates(self):
        """Test that we can detect duplicates talks and pages"""
        # Final chedule is
        #       Venue 1  Venue 2
        # 10-11 Talk 1   Page 1
        # 11-12 Talk 1   Page 1
        day1 = Day.objects.create(date=D.date(2013, 9, 22))
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue1.days.add(day1)
        venue2.days.add(day1)

        start1 = D.time(10, 0, 0)
        start2 = D.time(11, 0, 0)
        end = D.time(12, 0, 0)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2,
                                    day=day1)
        slot2 = Slot.objects.create(start_time=start1, end_time=end,
                                    day=day1)

        user = get_user_model().objects.create_user('john', 'best@wafer.test',
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

        all_items = prefetch_schedule_items()
        duplicates = find_duplicate_schedule_items(all_items)
        assert set(duplicates) == set([item1, item2])

        item3 = ScheduleItem.objects.create(venue=venue2,
                                            page_id=page1.pk)
        item3.slots.add(slot1)
        item4 = ScheduleItem.objects.create(venue=venue2,
                                            talk_id=talk.pk)
        item4.slots.add(slot2)

        all_items = prefetch_schedule_items()
        duplicates = find_duplicate_schedule_items(all_items)
        assert set(duplicates) == set([item1, item2, item4])

        item4.page_id = page2.pk
        item4.talk_id = None
        item4.save()

        all_items = prefetch_schedule_items()
        duplicates = find_duplicate_schedule_items(all_items)
        assert set(duplicates) == set([item1, item2])

    def test_venues(self):
        """Test that we detect venues violating the day constraints
           correctly."""
        day1 = Day.objects.create(date=D.date(2013, 9, 22))
        day2 = Day.objects.create(date=D.date(2013, 9, 23))
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue1.days.add(day1)
        venue2.days.add(day2)

        start1 = D.time(10, 0, 0)
        start2 = D.time(11, 0, 0)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2,
                                    day=day1)

        page = Page.objects.create(name="test page", slug="test")

        item1 = ScheduleItem.objects.create(venue=venue1,
                                            page_id=page.pk)
        item1.slots.add(slot1)

        item2 = ScheduleItem.objects.create(venue=venue2,
                                            page_id=page.pk)
        item2.slots.add(slot1)

        all_items = prefetch_schedule_items()
        # Needs to be an explicit list, as in the find_clashes test
        venues = list(find_invalid_venues(all_items))
        assert venues[0][0] == venue2
        assert set(venues[0][1]) == set([item2])

        slot2 = Slot.objects.create(start_time=start1, end_time=start2,
                                    day=day2)
        item3 = ScheduleItem.objects.create(venue=venue2, page_id=page.pk)

        item3.slots.add(slot2)
        all_items = prefetch_schedule_items()
        venues = list(find_invalid_venues(all_items))
        assert venues[0][0] == venue2
        assert set(venues[0][1]) == set([item2])

        item4 = ScheduleItem.objects.create(venue=venue1, page_id=page.pk)
        item5 = ScheduleItem.objects.create(venue=venue2, page_id=page.pk)

        item4.slots.add(slot2)
        item5.slots.add(slot1)
        all_items = prefetch_schedule_items()
        venues = list(find_invalid_venues(all_items))
        assert set([x[0] for x in venues]) == set([venue1, venue2])
        venue_1_items = []
        venue_2_items = []
        for sublist in venues:
            if sublist[0] == venue1:
                venue_1_items.extend(sublist[1])
            elif sublist[0] == venue2:
                venue_2_items.extend(sublist[1])
        assert set(venue_1_items) == set([item4])
        assert set(venue_2_items) == set([item2, item5])

    def test_validate_schedule(self):
        """Check the behaviour of validate schedule

           We also test check_schedule, since the logic of the two funcions
           is so similar it doesn't make sense to have a second test
           case for it."""
        day1 = Day.objects.create(date=D.date(2013, 9, 22))
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue1.days.add(day1)
        page = Page.objects.create(name="test page", slug="test")

        start1 = D.time(10, 0, 0)
        start2 = D.time(11, 0, 0)
        end = D.time(12, 0, 0)

        slot1 = Slot.objects.create(start_time=start1, end_time=start2,
                                    day=day1)
        slot2 = Slot.objects.create(start_time=start2, end_time=end,
                                    day=day1)

        item1 = ScheduleItem.objects.create(venue=venue1,
                                            page_id=page.pk,
                                            details="Item 1")
        # Create an invalid item
        item2 = ScheduleItem.objects.create(venue=venue1, details="Item 2")
        # Create a simple venue/slot clash
        item1.slots.add(slot1)
        item2.slots.add(slot1)
        # Schedule shoudln't validate
        check_schedule.invalidate()
        self.assertFalse(check_schedule())
        # Invalid item & clash should be reported
        errors = validate_schedule()
        self.assertEqual(len(errors), 2)
        # Fix the invalid item
        item2.page_id = page.pk
        item2.save()
        # Schedule is still invalid, but only the clash remains
        check_schedule.invalidate()
        self.assertFalse(check_schedule())
        errors = validate_schedule()
        self.assertEqual(len(errors), 1)
        # Fix clashes
        item2.slots.remove(slot1)
        item2.slots.add(slot2)
        item2.save()
        # Schedule should now be valid
        check_schedule.invalidate()
        self.assertTrue(check_schedule())
        errors = validate_schedule()
        self.assertEqual(len(errors), 0)
