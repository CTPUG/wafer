import datetime as D
from django.utils import timezone
from django.core.exceptions import ValidationError

from django.test import TestCase

from wafer.schedule.models import ScheduleBlock, Slot, ScheduleItem, Venue
from wafer.schedule.tests.test_views import make_pages, make_items


class BlockTests(TestCase):

    def setUp(self):
        """We run the tests in UTC, to be sane since we are using
           timezone aware dates."""
        timezone.activate('UTC')

    def test_blocks_single_days(self):
        """Create some days and check the results."""
        o1 = ScheduleBlock.objects.create(
                start_time=D.datetime(2013, 9, 22, 9, 0, 0,
                                      tzinfo=timezone.utc),
                end_time=D.datetime(2013, 9, 22, 19, 0, 0,
                                    tzinfo=timezone.utc))
        o2 = ScheduleBlock.objects.create(
                start_time=D.datetime(2013, 9, 23, 9, 0, 0,
                                      tzinfo=timezone.utc),
                end_time=D.datetime(2013, 9, 23, 19, 0, 0,
                                    tzinfo=timezone.utc))

        self.assertEqual(ScheduleBlock.objects.count(), 2)

        output = ["%s" % x for x in ScheduleBlock.objects.all()]

        self.assertEqual(output, ["Sep 22 (Sun)", "Sep 23 (Mon)"])

        # Cleanup
        o1.delete()
        o2.delete()

    def test_blocks_multiple_days(self):
        """Create 2 blocks that each cross midnight and check the results."""
        ScheduleBlock.objects.create(
                start_time=D.datetime(2013, 9, 22, 9, 0, 0,
                                      tzinfo=timezone.utc),
                end_time=D.datetime(2013, 9, 23, 3, 0, 0,
                                    tzinfo=timezone.utc))
        ScheduleBlock.objects.create(
                start_time=D.datetime(2013, 9, 23, 9, 0, 0,
                                      tzinfo=timezone.utc),
                end_time=D.datetime(2013, 9, 24, 3, 0, 0,
                                    tzinfo=timezone.utc))

        self.assertEqual(ScheduleBlock.objects.count(), 2)

        output = ["%s" % x for x in ScheduleBlock.objects.all()]

        self.assertEqual(output, ["Sep 22 (Sun) 09:00 - Sep 23 (Mon) 03:00",
                                  "Sep 23 (Mon) 09:00 - Sep 24 (Tue) 03:00"])

    def test_block_start_time_end_time_validation(self):
        """Test our blocks have start_time < end_time."""
        block1 = ScheduleBlock.objects.create(
                start_time=D.datetime(2013, 9, 22, 11, 0, 0,
                                      tzinfo=timezone.utc),
                end_time=D.datetime(2013, 9, 22, 9, 0, 0,
                                    tzinfo=timezone.utc))
        self.assertRaises(ValidationError, block1.clean)
        # Test across midnight
        block2 = ScheduleBlock.objects.create(
                start_time=D.datetime(2013, 9, 23, 1, 0, 0,
                                      tzinfo=timezone.utc),
                end_time=D.datetime(2013, 9, 22, 23, 0, 0,
                                    tzinfo=timezone.utc))
        self.assertRaises(ValidationError, block2.clean)

    def test_changing_block(self):
        """Test that we can update block info and have correct validation behavior."""
        block1 = ScheduleBlock.objects.create(
                start_time=D.datetime(2013, 9, 27, 11, 0, 0,
                                      tzinfo=timezone.utc),
                end_time=D.datetime(2013, 9, 27, 19, 0, 0,
                                    tzinfo=timezone.utc))
        block1.clean()
        block1.save()
        # These should work
        block1.start_time = D.datetime(2013, 9, 27, 9, 0, 0,
                                       tzinfo=timezone.utc)
        block1.clean()
        block1.save()
        block1.end_time = D.datetime(2013, 9, 27, 12, 0, 0,
                                     tzinfo=timezone.utc)
        block1.clean()
        block1.save()
        # This should fail
        block1.start_time = D.datetime(2013, 9, 27, 15, 0, 0,
                                       tzinfo=timezone.utc)
        self.assertRaises(ValidationError, block1.clean)

    def test_block_overlaps(self):
        """Test that we can't create overlapping blocks."""
        block1 = ScheduleBlock.objects.create(
                start_time=D.datetime(2013, 9, 22, 1, 0, 0,
                                      tzinfo=timezone.utc),
                end_time=D.datetime(2013, 9, 22, 19, 0, 0,
                                    tzinfo=timezone.utc))
        # Test starting in the block
        block2 = ScheduleBlock.objects.create(
                start_time=D.datetime(2013, 9, 22, 11, 0, 0,
                                      tzinfo=timezone.utc),
                end_time=D.datetime(2013, 9, 22, 23, 0, 0,
                                    tzinfo=timezone.utc))
        self.assertRaises(ValidationError, block2.clean)
        # Test ending in the block
        block2 = ScheduleBlock.objects.create(
                start_time=D.datetime(2013, 9, 22, 0, 30, 0,
                                      tzinfo=timezone.utc),
                end_time=D.datetime(2013, 9, 22, 11, 0, 0,
                                    tzinfo=timezone.utc))
        self.assertRaises(ValidationError, block2.clean)
        # Test across midnight
        block2 = ScheduleBlock.objects.create(
                start_time=D.datetime(2013, 9, 22, 11, 0, 0,
                                      tzinfo=timezone.utc),
                end_time=D.datetime(2013, 9, 23, 23, 0, 0,
                                    tzinfo=timezone.utc))
        self.assertRaises(ValidationError, block2.clean)
        # Test included block
        block2 = ScheduleBlock.objects.create(
                start_time=D.datetime(2013, 9, 22, 3, 0, 0,
                                      tzinfo=timezone.utc),
                end_time=D.datetime(2013, 9, 22, 4, 0, 0,
                                    tzinfo=timezone.utc))
        self.assertRaises(ValidationError, block2.clean)
        # Test surrounding block
        block2 = ScheduleBlock.objects.create(
                start_time=D.datetime(2013, 9, 22, 0, 15, 0,
                                      tzinfo=timezone.utc),
                end_time=D.datetime(2013, 9, 23, 4, 0, 0,
                                    tzinfo=timezone.utc))
        self.assertRaises(ValidationError, block2.clean)


class SlotTests(TestCase):

    def test_simple(self):
        """Test we can assign slots to a Block that spans only few hours."""
        block1 = ScheduleBlock.objects.create(
                start_time=D.datetime(2013, 9, 22, 9, 0, 0,
                                      tzinfo=timezone.utc),
                end_time=D.datetime(2013, 9, 22, 19, 0, 0,
                                    tzinfo=timezone.utc))
        slot1 = Slot(start_time=D.datetime(2013, 9, 22, 9, 0, 0,
                                           tzinfo=timezone.utc),
                     end_time=D.datetime(2013, 9, 22, 10, 20, 0,
                                         tzinfo=timezone.utc))
        self.assertEqual(slot1.get_block(), block1)
        self.assertEqual(slot1.get_duration(), {'hours': 1,
                                                'minutes': 20})
        # Check end and start times
        slot2 = Slot(start_time=D.datetime(2013, 9, 22, 12, 0, 0,
                                           tzinfo=timezone.utc),
                     end_time=D.datetime(2013, 9, 22, 13, 0, 0,
                                         tzinfo=timezone.utc))
        slot3 = Slot(start_time=D.datetime(2013, 9, 22, 18, 30, 0,
                                           tzinfo=timezone.utc),
                     end_time=D.datetime(2013, 9, 22, 19, 0, 0,
                                         tzinfo=timezone.utc))
        self.assertEqual(slot2.get_block(), block1)
        self.assertEqual(slot2.get_duration(), {'hours': 1,
                                                'minutes': 0})
        self.assertEqual(slot3.get_block(), block1)
        self.assertEqual(slot3.get_duration(), {'hours': 0,
                                                'minutes': 30})
        block1.delete()

    def test_midnight(self):
        """Test that we can assign slots that span midnight to a block
           that spans midnight."""
        block1 = ScheduleBlock.objects.create(
                start_time=D.datetime(2013, 9, 22, 9, 0, 0,
                                      tzinfo=timezone.utc),
                end_time=D.datetime(2013, 9, 23, 8, 0, 0,
                                    tzinfo=timezone.utc))
        slot1 = Slot(start_time=D.datetime(2013, 9, 22, 23, 0, 0,
                                           tzinfo=timezone.utc),
                     end_time=D.datetime(2013, 9, 23, 1, 0, 0,
                                         tzinfo=timezone.utc))
        self.assertEqual(slot1.get_block(), block1)
        self.assertEqual(slot1.get_duration(), {'hours': 2,
                                                'minutes': 0})
        block1.delete()

    def test_changing_slots(self):
        """Test that we can update slots and get the correct validation behaviour."""
        block1 = ScheduleBlock.objects.create(
                start_time=D.datetime(2013, 9, 26, 9, 0, 0,
                                      tzinfo=timezone.utc),
                end_time=D.datetime(2013, 9, 26, 19, 0, 0,
                                    tzinfo=timezone.utc))
        slot1 = Slot(start_time=D.datetime(2013, 9, 26, 10, 0,
                                           tzinfo=timezone.utc),
                     end_time=D.datetime(2013, 9, 26, 12, 0, 0,
                                         tzinfo=timezone.utc))
        slot1.clean()
        slot1.save()
        # This should work
        slot1.start_time = D.datetime(2013, 9, 26, 9, 0, 0,
                                      tzinfo=timezone.utc)
        slot1.clean()
        slot1.save()
        slot1.end_time = D.datetime(2013, 9, 26, 11, 0, 0,
                                    tzinfo=timezone.utc)
        slot1.clean()
        slot1.save()
        # This should fail
        slot1.start_time = D.datetime(2013, 9, 26, 12, 0, 0,
                                      tzinfo=timezone.utc)
        self.assertRaises(ValidationError, slot1.clean)
        slot1.delete()
        block1.delete()

    def test_overlapping_slots(self):
        """Test that we can't create overlapping slots."""
        block1 = ScheduleBlock.objects.create(
                start_time=D.datetime(2013, 9, 26, 9, 0, 0,
                                      tzinfo=timezone.utc),
                end_time=D.datetime(2013, 9, 26, 19, 0, 0,
                                    tzinfo=timezone.utc))
        slot1 = Slot(start_time=D.datetime(2013, 9, 26, 10, 0,
                                           tzinfo=timezone.utc),
                     end_time=D.datetime(2013, 9, 26, 12, 0, 0,
                                         tzinfo=timezone.utc))
        slot1.clean()
        slot1.save()
        # Start time is in the middle of slot1
        slot2 = Slot(start_time=D.datetime(2013, 9, 26, 11, 0, 0,
                                           tzinfo=timezone.utc),
                     end_time=D.datetime(2013, 9, 26, 13, 0, 0,
                                         tzinfo=timezone.utc))
        self.assertRaises(ValidationError, slot2.clean)
        # End time is in the middle of slot2
        slot2 = Slot(start_time=D.datetime(2013, 9, 26, 9, 0, 0,
                                           tzinfo=timezone.utc),
                     end_time=D.datetime(2013, 9, 26, 11, 0, 0,
                                         tzinfo=timezone.utc))
        self.assertRaises(ValidationError, slot2.clean)
        # Slot 2 totally encloses slot 1
        slot2 = Slot(start_time=D.datetime(2013, 9, 26, 9, 0, 0,
                                           tzinfo=timezone.utc),
                     end_time=D.datetime(2013, 9, 26, 13, 0, 0,
                                         tzinfo=timezone.utc))
        self.assertRaises(ValidationError, slot2.clean)
        # Slot 2 totally included in slot 1
        slot2 = Slot(start_time=D.datetime(2013, 9, 26, 11, 30, 0,
                                           tzinfo=timezone.utc),
                     end_time=D.datetime(2013, 9, 26, 12, 30, 0,
                                         tzinfo=timezone.utc))
        self.assertRaises(ValidationError, slot2.clean)
        # Slot 2 has the same times as slot 1
        slot2 = Slot(start_time=D.datetime(2013, 9, 26, 11, 0, 0,
                                           tzinfo=timezone.utc),
                     end_time=D.datetime(2013, 9, 26, 13, 0, 0,
                                         tzinfo=timezone.utc))
        self.assertRaises(ValidationError, slot2.clean)
        # Check we don't raise errors on slots that touch as intended
        # slot 1 start time is slot 2's end time
        slot2 = Slot(start_time=D.datetime(2013, 9, 26, 9, 0, 0,
                                           tzinfo=timezone.utc),
                     end_time=D.datetime(2013, 9, 26, 10, 0, 0,
                                         tzinfo=timezone.utc))
        slot2.clean()
        slot2.save()
        # slot 1 end time is slot 2's start time
        slot3 = Slot(start_time=D.datetime(2013, 9, 26, 12, 0, 0,
                                           tzinfo=timezone.utc),
                     end_time=D.datetime(2013, 9, 26, 13, 0, 0,
                                         tzinfo=timezone.utc))
        slot3.clean()

        slot1.delete()
        slot2.delete()
        block1.delete()

    def test_previous_overlaps(self):
        """Test that we handle overlap checks involving editing
           previous slots correctly."""

        block1 = ScheduleBlock.objects.create(
                start_time=D.datetime(2013, 9, 26, 9, 0, 0,
                                      tzinfo=timezone.utc),
                end_time=D.datetime(2013, 9, 26, 19, 0, 0,
                                    tzinfo=timezone.utc))
        slot1 = Slot(start_time=D.datetime(2013, 9, 26, 10, 0,
                                           tzinfo=timezone.utc),
                     end_time=D.datetime(2013, 9, 26, 12, 0, 0,
                                         tzinfo=timezone.utc))
        slot1.clean()
        slot1.save()
        slot2 = Slot(previous_slot=slot1,
                     end_time=D.datetime(2013, 9, 26, 13, 0, 0,
                                         tzinfo=timezone.utc))
        slot2.clean()
        slot2.save()

        # Check that updating slot1's end_time to 12:30 works as expected
        slot1.end_time = D.datetime(2013, 9, 26, 12, 30, 0, tzinfo=timezone.utc)
        slot1.clean()
        slot1.save()

        self.assertEqual(slot2.get_start_time(),
                         D.datetime(2013, 9, 26, 12, 30, 0,
                                    tzinfo=timezone.utc))

        # Check that updating slot1's end_time to 13:30 fails, though
        slot1.end_time = D.datetime(2013, 9, 26, 13, 30, 0, tzinfo=timezone.utc)
        self.assertRaises(ValidationError, slot1.clean)

    def test_invalid_slot(self):
        """Test that slots must have start time > end_time"""
        # Same day
        block1 = ScheduleBlock.objects.create(
                start_time=D.datetime(2013, 9, 22, 9, 0, 0,
                                      tzinfo=timezone.utc),
                end_time=D.datetime(2013, 9, 22, 19, 0, 0,
                                    tzinfo=timezone.utc))
        slot1 = Slot(start_time=D.datetime(2013, 9, 22, 11, 0,
                                           tzinfo=timezone.utc),
                     end_time=D.datetime(2013, 9, 22, 10, 0, 0,
                                         tzinfo=timezone.utc))
        self.assertRaises(ValidationError, slot1.clean)
        block2 = ScheduleBlock.objects.create(
                start_time=D.datetime(2013, 9, 24, 9, 0, 0,
                                      tzinfo=timezone.utc),
                end_time=D.datetime(2013, 9, 25, 19, 0, 0,
                                    tzinfo=timezone.utc))
        # Different day,
        slot2 = Slot(start_time=D.datetime(2013, 9, 25, 1, 0, 0,
                                           tzinfo=timezone.utc),
                     end_time=D.datetime(2013, 9, 24, 3, 0, 0,
                                         tzinfo=timezone.utc))
        self.assertRaises(ValidationError, slot2.clean)

        block1.delete()
        block2.delete()

    def test_invalid_slot_block(self):
        """Test that we can't create a slot outside the block's times"""
        block1 = ScheduleBlock.objects.create(
                start_time=D.datetime(2013, 9, 22, 9, 0, 0,
                                      tzinfo=timezone.utc),
                end_time=D.datetime(2013, 9, 22, 18, 0, 0,
                                    tzinfo=timezone.utc))
        # Totally after
        slot1 = Slot(start_time=D.datetime(2013, 9, 22, 23, 0, 0,
                                           tzinfo=timezone.utc),
                     end_time=D.datetime(2013, 9, 23, 1, 0, 0,
                                         tzinfo=timezone.utc))
        self.assertRaises(ValidationError, slot1.clean)
        # Totally before
        slot2 = Slot(start_time=D.datetime(2013, 9, 21, 23, 0, 0,
                                           tzinfo=timezone.utc),
                     end_time=D.datetime(2013, 9, 21, 1, 0, 0,
                                         tzinfo=timezone.utc))
        self.assertRaises(ValidationError, slot2.clean)
        # Overlaps the end
        slot3 = Slot(start_time=D.datetime(2013, 9, 22, 17, 0, 0,
                                           tzinfo=timezone.utc),
                     end_time=D.datetime(2013, 9, 22, 19, 0, 0,
                                         tzinfo=timezone.utc))
        self.assertRaises(ValidationError, slot3.clean)
        # Overlaps the start
        slot4 = Slot(start_time=D.datetime(2013, 9, 22, 7, 0, 0,
                                           tzinfo=timezone.utc),
                     end_time=D.datetime(2013, 9, 22, 10, 0, 0,
                                         tzinfo=timezone.utc))
        self.assertRaises(ValidationError, slot4.clean)


class LastUpdateTests(TestCase):

    def setUp(self):
        """Create some slots and schedule items"""
        timezone.activate('UTC')
        block1 = ScheduleBlock.objects.create(
                start_time=D.datetime(2013, 9, 22, 9, 0, 0,
                                      tzinfo=timezone.utc),
                end_time=D.datetime(2013, 9, 22, 19, 0, 0,
                                    tzinfo=timezone.utc))
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue1.blocks.add(block1)
        venue2.blocks.add(block1)

        start1 = D.datetime(2013, 9, 22, 10, 0, 0,
                            tzinfo=timezone.utc)
        start2 = D.datetime(2013, 9, 22, 11, 0, 0,
                            tzinfo=timezone.utc)
        start3 = D.datetime(2013, 9, 22, 12, 0, 0,
                            tzinfo=timezone.utc)
        start4 = D.datetime(2013, 9, 22, 13, 0, 0,
                            tzinfo=timezone.utc)
        start5 = D.datetime(2013, 9, 22, 14, 0, 0,
                            tzinfo=timezone.utc)
        self.slots = []
        self.slots.append(Slot.objects.create(start_time=start1,
                                              end_time=start2))
        self.slots.append(Slot.objects.create(start_time=start2,
                                              end_time=start3))
        self.slots.append(Slot.objects.create(start_time=start3,
                                              end_time=start4))
        self.slots.append(Slot.objects.create(start_time=start4,
                                              end_time=start5))

        pages = make_pages(8)
        venues = [venue1, venue2] * 4
        self.items = make_items(venues, pages)

        for index, item in enumerate(self.items):
            item.slots.add(self.slots[index // 2])

    def test_item_save(self):
        """Test that the last update value is correctly updated on save."""
        last_updated = self.items[0].last_updated
        self.items[0].save()
        self.assertNotEqual(last_updated, self.items[0].last_updated)
        last_updated = self.items[0].last_updated
        self.items[0].save(update_fields=['last_updated'])
        self.assertNotEqual(last_updated, self.items[0].last_updated)

    def test_slot_save_no_next_slot(self):
        """Check that we handle a slot hierachy just using times as expected"""
        update_times = {}
        for item in ScheduleItem.objects.all():
            update_times[item.pk] = item.last_updated

        self.slots[0].name = 'New name'
        self.slots[0].save()
        # Check that we've changed all items associated with this slot, but
        # not any of the other (no next/previous slot relationships exist)
        for item in ScheduleItem.objects.all():
            if self.slots[0] == item.slots.all()[0]:
                self.assertNotEqual(item.last_updated, update_times[item.pk])
            else:
                self.assertEqual(item.last_updated, update_times[item.pk])

    def test_slot_save_prev_next(self):
        """Check we update current and next slot items as expected."""
        self.slots[1].start_time = None
        self.slots[1].previous_slot = self.slots[0]
        self.slots[1].save()
        self.slots[2].start_time = None
        self.slots[2].previous_slot = self.slots[1]
        self.slots[2].save()

        update_times = {}
        for item in ScheduleItem.objects.all():
            update_times[item.pk] = item.last_updated

        self.slots[0].name = 'New name'
        self.slots[0].save()
        # Check that we've changed all items associated with this slot, but
        # not any of the other (no next/previous slot relationships exist)
        for item in ScheduleItem.objects.all():
            if self.slots[0] == item.slots.all()[0]:
                self.assertNotEqual(item.last_updated, update_times[item.pk])
            elif self.slots[1] == item.slots.all()[0]:
                # Next slot, so items should have changed
                self.assertNotEqual(item.last_updated, update_times[item.pk])
            else:
                # No other items should have changed, as time changes don't
                # cascade that way
                self.assertEqual(item.last_updated, update_times[item.pk])


class ScheduleItemGUIDTests(TestCase):
    def setUp(self):
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        self.venues = [venue1]

    def test_unique_guid(self):
        """Test that the all guids are unique."""
        pages = make_pages(2)
        items = make_items(self.venues * 2, pages)

        guids = set(item.guid for item in items)
        self.assertEqual(len(guids), len(items))

    def test_rescheduled_page_keeps_guid(self):
        """A page that's in the schedule once keeps its guid when rescheduled"""
        pages = make_pages(2)
        items = make_items(self.venues * 2, pages)
        guid = items[0].guid
        # Reschedule
        for item in items:
            item.delete()
        items = make_items(self.venues, pages)
        self.assertEqual(guid, items[0].guid)

    def test_double_scheduled_page_has_unique_guid(self):
        """A page that's in the schedule twice has a unique GUID per instance"""
        pages = make_pages(1)
        items = make_items(self.venues * 2, pages * 2)
        self.assertNotEqual(items[0].guid, items[1].guid)
