import datetime as D

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.http import HttpRequest

from wafer.pages.models import Page
from wafer.schedule.admin import (
    SlotAdmin, find_overlapping_slots, validate_items,
    find_duplicate_schedule_items, find_clashes, find_invalid_venues,
    find_non_contiguous)
from wafer.schedule.models import Day, Venue, Slot, ScheduleItem
from wafer.talks.models import Talk, ACCEPTED, REJECTED, PENDING


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

        overlaps = find_overlapping_slots()
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

        overlaps = find_overlapping_slots()
        assert overlaps == set([slot4, slot5])

        # Test no overlap
        slot5.start_time = start3
        slot5.end_time = start4
        slot5.save()
        overlaps = find_overlapping_slots()
        assert len(overlaps) == 0

        # Test common end time
        slot5.end_time = start5
        slot5.save()
        overlaps = find_overlapping_slots()
        assert overlaps == set([slot4, slot5])

        # Test overlap detect with previous slot set
        slot5.start_time = None
        slot5.end_time = start5
        slot5.previous_slot = slot1
        slot5.save()
        overlaps = find_overlapping_slots()
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

        invalid = validate_items()
        assert set(invalid) == set([item1])

        item2 = ScheduleItem.objects.create(venue=venue1,
                                            talk_id=talk.pk)
        item2.slots.add(slot2)

        # Test talk status
        talk.status = REJECTED
        talk.save()
        invalid = validate_items()
        assert set(invalid) == set([item1, item2])

        talk.status = PENDING
        talk.save()
        invalid = validate_items()
        assert set(invalid) == set([item1, item2])

        talk.status = ACCEPTED
        talk.save()
        invalid = validate_items()
        assert set(invalid) == set([item1])

        item3 = ScheduleItem.objects.create(venue=venue1,
                                            talk_id=None, page_id=None)
        item3.slots.add(slot2)

        invalid = validate_items()
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

        invalid = find_non_contiguous()
        # Only item1 is invalid
        assert set(invalid) == set([item1])

        item1.slots.add(slot2)
        item1.slots.remove(slot1)
        item2.slots.add(slot1)
        item2.slots.remove(slot2)

        invalid = validate_items()
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

        duplicates = find_duplicate_schedule_items()
        assert set(duplicates) == set([item1, item2])

        item3 = ScheduleItem.objects.create(venue=venue2,
                                            page_id=page1.pk)
        item3.slots.add(slot1)
        item4 = ScheduleItem.objects.create(venue=venue2,
                                            talk_id=talk.pk)
        item4.slots.add(slot2)

        duplicates = find_duplicate_schedule_items()
        assert set(duplicates) == set([item1, item2, item4])

        item4.page_id = page2.pk
        item4.talk_id = None
        item4.save()

        duplicates = find_duplicate_schedule_items()
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

        venues = find_invalid_venues()
        assert set(venues) == set([venue2])
        assert set(venues[venue2]) == set([item2])

        slot2 = Slot.objects.create(start_time=start1, end_time=start2,
                                    day=day2)
        item3 = ScheduleItem.objects.create(venue=venue2, page_id=page.pk)

        item3.slots.add(slot2)
        venues = find_invalid_venues()
        assert set(venues) == set([venue2])
        assert set(venues[venue2]) == set([item2])

        item4 = ScheduleItem.objects.create(venue=venue1, page_id=page.pk)
        item5 = ScheduleItem.objects.create(venue=venue2, page_id=page.pk)

        item4.slots.add(slot2)
        item5.slots.add(slot1)
        venues = find_invalid_venues()
        assert set(venues) == set([venue1, venue2])
        assert set(venues[venue1]) == set([item4])
        assert set(venues[venue2]) == set([item2, item5])
