import datetime as D

from django.test import TestCase

from wafer.schedule.models import Day, Slot, ScheduleItem, Venue
from wafer.schedule.tests.test_views import make_pages, make_items


class DayTests(TestCase):
    def test_days(self):
        """Create some days and check the results."""
        Day.objects.create(date=D.date(2013, 9, 22))
        Day.objects.create(date=D.date(2013, 9, 23))

        assert Day.objects.count() == 2

        output = ["%s" % x for x in Day.objects.all()]

        assert output == ["Sep 22 (Sun)", "Sep 23 (Mon)"]


class LastUpdateTests(TestCase):

    def setUp(self):
        """Create some slots and schedule items"""
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
        self.slots = []
        self.slots.append(Slot.objects.create(start_time=start1,
                                              end_time=start2, day=day1))
        self.slots.append(Slot.objects.create(start_time=start2,
                                              end_time=start3, day=day1))
        self.slots.append(Slot.objects.create(start_time=start3,
                                              end_time=start4, day=day1))
        self.slots.append(Slot.objects.create(start_time=start4,
                                              end_time=start5, day=day1))

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
