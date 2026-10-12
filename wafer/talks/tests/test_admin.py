# Test the talk list filters

from django.test import TestCase
from django.utils import version

from wafer.talks.models import (ACCEPTED, REJECTED, CANCELLED, SUBMITTED,
                                UNDER_CONSIDERATION, Talk)
from wafer.talks.admin import (HasNotesFilter, ScheduleDuplicatesFilter, TalkAdmin)
from wafer.talks.tests.fixtures import create_talk


class TalkAdminTests(TestCase):

    def setUp(self):
        """Create several talks"""
        self.talk_a = create_talk("Talk A", ACCEPTED, "author_a")
        self.talk_r = create_talk("Talk R", REJECTED, "author_r")
        self.talk_s = create_talk("Talk S", SUBMITTED, "author_s")
        self.talk_u = create_talk("Talk U", UNDER_CONSIDERATION, "author_u")
        self.talk_c = create_talk("Talk c", CANCELLED, "author_c")
        self.admin = TalkAdmin(Talk, None)

    def _make_notes_filter(self, notes):
        """Helper to handle version differences in creating filters"""
        value = notes
        if version.get_complete_version()[0] >= 5:
            value = [value]
        return HasNotesFilter(None, {'has_notes': value}, Talk, self.admin)

    def _make_duplicates_filter(self, notes):
        """Helper to handle version differences in creating filters"""
        value = notes
        if version.get_complete_version()[0] >= 5:
            value = [value]
        return ScheduleDuplicatesFilter(None, {'num_schedulable': value}, Talk, self.admin)

    def test_has_notes_filter(self):
        """Test that we can filter the talk list on notes"""
        TestFilter = self._make_notes_filter('yes')
        # Currently should be all the talks
        filtered = TestFilter.queryset(None, Talk.objects.all())
        self.assertEqual(len(filtered), 5)
        # Remove a note
        self.talk_c.notes = ""
        self.talk_c.save()
        filtered = TestFilter.queryset(None, Talk.objects.all())
        self.assertEqual(len(filtered), 4)
        # Change a note
        self.talk_a.notes = "Good talk"
        self.talk_a.save()
        filtered = TestFilter.queryset(None, Talk.objects.all())
        self.assertEqual(len(filtered), 4)
        TestFilter = self._make_notes_filter('no')
        filtered = TestFilter.queryset(None, Talk.objects.all())
        self.assertEqual(len(filtered), 1)
        # Remove another note
        self.talk_r.notes = ""
        self.talk_r.save()
        filtered = TestFilter.queryset(None, Talk.objects.all())
        self.assertEqual(len(filtered), 2)

    def test_duplicates_filter(self):
        """Test that we can filter the talk list on duplicates allowed"""
        TestFilter = self._make_duplicates_filter('1')
        # Currently should be all the talks
        filtered = TestFilter.queryset(None, Talk.objects.all())
        self.assertEqual(len(filtered), 5)
        # Disallow a talk from the schedule
        self.talk_r.num_schedulable = 0
        self.talk_r.save()
        filtered = TestFilter.queryset(None, Talk.objects.all())
        self.assertEqual(len(filtered), 4)
        # Check disallowed talks
        TestFilter = self._make_duplicates_filter('0')
        filtered = TestFilter.queryset(None, Talk.objects.all())
        self.assertEqual(len(filtered), 1)
        self.assertEqual(list(filtered), [self.talk_r])
        # Add a talk with mutiplie duplicates
        self.talk_a.num_schedulable = 3
        self.talk_a.save()
        # Talk should be in the 'duplicates allowed list'
        TestFilter = self._make_duplicates_filter('2')
        filtered = TestFilter.queryset(None, Talk.objects.all())
        self.assertEqual(len(filtered), 1)
        self.assertEqual(list(filtered), [self.talk_a])
        # Talk should be removed from the 'no duplicates allowed list'
        TestFilter = self._make_duplicates_filter('1')
        filtered = TestFilter.queryset(None, Talk.objects.all())
        self.assertEqual(len(filtered), 3)

