import datetime as D
from django.utils import timezone

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

class LastUpdateTests(TestCase):

    def setUp(self):
        """Create some slots and schedule items"""
        timezone.activate('UTC')
        day1 = ScheduleBlock.objects.create(
                start_time=D.datetime(2013, 9, 22, 9, 0, 0,
                                      tzinfo=timezone.utc),
                end_time=D.datetime(2013, 9, 22, 19, 0, 0,
                                    tzinfo=timezone.utc))
        day2 = ScheduleBlock.objects.create(
                start_time=D.datetime(2013, 9, 23, 9, 0, 0,
                                      tzinfo=timezone.utc),
                end_time=D.datetime(2013, 9, 23, 19, 0, 0,
                                    tzinfo=timezone.utc))
        venue1 = Venue.objects.create(order=1, name='Venue 1')
        venue2 = Venue.objects.create(order=2, name='Venue 2')
        venue1.blocks.add(day1)
        venue2.blocks.add(day1)

        start1 = D.datetime(2013, 9, 23, 10, 0, 0,
                            tzinfo=timezone.utc)
        start2 = D.datetime(2013, 9, 23, 11, 0, 0, 
                            tzinfo=timezone.utc)
        start3 = D.datetime(2013, 9, 23, 12, 0, 0,
                            tzinfo=timezone.utc)
        start4 = D.datetime(2013, 9, 23, 13, 0, 0,
                            tzinfo=timezone.utc)
        start5 = D.datetime(2013, 9, 23, 14, 0, 0,
                            tzinfo=timezone.utc)
        self.slots = []
        self.slots.append(Slot.objects.create(start_time=start1,
                                              end_time=start2, block=day1))
        self.slots.append(Slot.objects.create(start_time=start2,
                                              end_time=start3, block=day1))
        self.slots.append(Slot.objects.create(start_time=start3,
                                              end_time=start4, block=day1))
        self.slots.append(Slot.objects.create(start_time=start4,
                                              end_time=start5, block=day1))

        pages = make_pages(8)
        venues = [venue1, venue2] * 4
        self.items = make_items(venues, pages)

        for index, item in enumerate(self.items):
            item.slots.add(self.slots[index // 2])

    def test_item_save(self):
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
