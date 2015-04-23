from django.test import TestCase
from django.http import HttpRequest

import datetime as D
from wafer.schedule.admin import SlotAdmin
from wafer.schedule.models import Day, Slot


class DummyForm(object):

    def __init__(self):
        self.cleaned_data = {}


def make_dummy_form(additional):
    """Fake a form object for the tests"""
    form = DummyForm()
    form.cleaned_data['additional'] = additional
    return form


# Tests the custom save_model logic on SlotAdmin
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
