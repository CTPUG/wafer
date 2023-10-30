import datetime as D
from django.utils import timezone

from django.test import TestCase

from wafer.tests.utils import create_user
from wafer.talks.tests.fixtures import create_talk
from wafer.talks.models import ACCEPTED, CANCELLED, REJECTED

from wafer.schedule.models import ScheduleBlock, Slot, ScheduleItem, Venue
from wafer.schedule.admin import (find_clashes, find_invalid_venues, validate_items,
                                  find_duplicate_schedule_items, find_speaker_clashes,
                                  prefetch_schedule_items)
from wafer.schedule.tests.test_views import make_pages, make_items


def get_new_result(result, old_result):
    """Helper method so we're robust against the influence of database
       ordering on the results"""
    old_keys = set(x[0] for x in old_result)
    return [x for x in result if x[0] not in old_keys]


class ScheduleValidationTests(TestCase):
    """Test that various validators pick up the correct errors"""


    def setUp(self):
        """Create some blocks, slots and talks to work with"""
        timezone.activate('UTC')
        self.block1 = ScheduleBlock.objects.create(
                start_time=D.datetime(2013, 9, 22, 9, 0, 0,
                                      tzinfo=D.timezone.utc),
                end_time=D.datetime(2013, 9, 22, 19, 0, 0,
                                    tzinfo=D.timezone.utc))
        self.block2 = ScheduleBlock.objects.create(
                start_time=D.datetime(2013, 9, 23, 9, 0, 0,
                                      tzinfo=D.timezone.utc),
                end_time=D.datetime(2013, 9, 23, 19, 0, 0,
                                    tzinfo=D.timezone.utc))

        self.venue1 = Venue.objects.create(order=1, name='Venue 1')
        self.venue2 = Venue.objects.create(order=2, name='Venue 2')
        self.venue3 = Venue.objects.create(order=3, name='Venue 3')
        self.venue1.blocks.add(self.block1)
        self.venue2.blocks.add(self.block1)
        self.venue3.blocks.add(self.block2)

        start1 = D.datetime(2013, 9, 22, 10, 0, 0,
                            tzinfo=D.timezone.utc)
        start2 = D.datetime(2013, 9, 22, 11, 0, 0,
                            tzinfo=D.timezone.utc)
        start3 = D.datetime(2013, 9, 22, 12, 0, 0,
                            tzinfo=D.timezone.utc)
        start4 = D.datetime(2013, 9, 22, 13, 0, 0,
                            tzinfo=D.timezone.utc)
        start5 = D.datetime(2013, 9, 22, 14, 0, 0,
                            tzinfo=D.timezone.utc)
        self.slots = []
        self.slots.append(Slot.objects.create(start_time=start1,
                                              end_time=start2))
        self.slots.append(Slot.objects.create(start_time=start2,
                                              end_time=start3))
        self.slots.append(Slot.objects.create(start_time=start3,
                                              end_time=start4))
        self.slots.append(Slot.objects.create(start_time=start4,
                                              end_time=start5))
        self.pages = make_pages(8)
        venues = [self.venue1, self.venue2] * 4
        self.items = make_items(venues, self.pages)

        for index, item in enumerate(self.items):
            item.slots.add(self.slots[index // 2])

        self.author1 = create_user('Author 1')
        self.author2 = create_user('Author 2')
        self.author3 = create_user('Author 3')
        self.author4 = create_user('Author 4')
        self.author5 = create_user('Author 5')

        self.talk1 = create_talk('Talk 1', ACCEPTED, user=self.author1)
        self.talk2 = create_talk('Talk 2', ACCEPTED, user=self.author2)
        self.talk3 = create_talk('Talk 3', ACCEPTED, user=self.author3)
        self.talk4 = create_talk('Talk 4', ACCEPTED, user=self.author4)
        self.talk5 = create_talk('Talk 5', ACCEPTED, user=self.author5)
        self.talk6 = create_talk('Talk 6', ACCEPTED, user=self.author1)

    def test_invalid_venue(self):
        """Test that the `find_invalid_venues` validator detects broken slots"""
        # Assert that everything is OK at the start
        all_items = prefetch_schedule_items()
        self.assertEqual(list(find_invalid_venues(all_items)), [])
        # Create an invalid slot/venue combination
        wrong_venue_item = ScheduleItem.objects.create(venue=self.venue3,
                                                       details="Invalid venue item",
                                                       page_id=self.pages[0].pk)
        wrong_venue_item.slots.add(self.slots[1])
        all_items = prefetch_schedule_items()
        result = list(find_invalid_venues(all_items))
        self.assertEqual(len(result), 1)
        self.assertEqual(self.venue3, result[0][0])
        self.assertIn(wrong_venue_item, result[0][1])

    def test_find_clashes(self):
        """Test that the `find_clashes` validator finds items that clash"""
        # Assert that everything is OK at the start
        all_items = prefetch_schedule_items()
        self.assertEqual(list(find_clashes(all_items)), [])
        # Create a duplicate item
        duplicate_item = ScheduleItem.objects.create(venue=self.venue2,
                                                     details="Duplicate item",
                                                     page_id=self.pages[0].pk)
        duplicate_item.slots.add(self.slots[1])
        all_items = prefetch_schedule_items()
        result = list(find_clashes(all_items))
        self.assertEqual(len(result), 1)
        self.assertIn(self.venue2, result[0][0])
        self.assertIn(self.slots[1], result[0][0])
        # We should have 2 duplicate items listed
        self.assertEqual(len(result[0][1]), 2)
        self.assertIn(duplicate_item, result[0][1])

    def test_duplicate_schedule_items(self):
        """Test that the `find_duplicate_schedule_items` validator finds
           talks that are assigned to multiple schedule items"""
        all_items = prefetch_schedule_items()
        self.assertEqual(list(find_duplicate_schedule_items(all_items)), [])
        # Create a clash assigning a talk to 2 items
        self.items[0].page_id = None
        self.items[0].talk_id = self.talk1.pk
        self.items[0].save()

        self.items[6].page_id = None
        self.items[6].talk_id = self.talk1.pk
        self.items[6].save()

        all_items = prefetch_schedule_items()
        result = list(find_duplicate_schedule_items(all_items))
        self.assertEqual(len(result), 2)
        self.assertIn(self.items[0], result)
        self.assertIn(self.items[6], result)

    def test_validate_items(self):
        """Test that the `validate_items` check works"""
        rejected_talk = create_talk('Talk Rejected', REJECTED, user=self.author1)
        cancelled_talk = create_talk('Talk Rejected', CANCELLED, user=self.author1)

        all_items = prefetch_schedule_items()
        self.assertEqual(list(validate_items(all_items)), [])

        # Check that a cancelled talk doesn't fail
        self.items[7].page_id = None
        self.items[7].talk_id = cancelled_talk.pk
        self.items[7].save()
        all_items = prefetch_schedule_items()
        self.assertEqual(list(validate_items(all_items)), [])

        # Test schedule item with no talk or page fail
        self.items[0].page_id = None
        self.items[0].save()
        all_items = prefetch_schedule_items()
        result = list(validate_items(all_items))
        self.assertEqual(len(result), 1)
        self.assertIn(self.items[0], result)

        # Test that schedule item with both a talk and page fails
        self.items[1].page_id = self.pages[0].pk
        self.items[1].talk_id = self.talk1.pk
        self.items[1].save()
        all_items = prefetch_schedule_items()
        result = list(validate_items(all_items))
        self.assertEqual(len(result), 2)
        self.assertIn(self.items[0], result)
        self.assertIn(self.items[1], result)

        # Test that a rejected talk on the schedule fails
        self.items[2].page_id = None
        self.items[2].talk_id = rejected_talk.pk
        self.items[2].save()
        all_items = prefetch_schedule_items()
        result = list(validate_items(all_items))
        self.assertEqual(len(result), 3)
        self.assertIn(self.items[0], result)
        self.assertIn(self.items[1], result)
        self.assertIn(self.items[2], result)

    def test_find_speaker_clashes(self):
        """Test the the `find_spekaer_clashes` check works"""
        # Replace some pages with talks and check that it is valid
        self.items[0].page_id = None
        self.items[0].talk_id = self.talk1.pk
        self.items[0].save()

        self.items[1].page_id = None
        self.items[1].talk_id = self.talk2.pk
        self.items[1].save()

        self.items[2].page_id = None
        self.items[2].talk_id = self.talk3.pk
        self.items[2].save()

        self.items[3].page_id = None
        self.items[3].talk_id = self.talk4.pk
        self.items[3].save()

        self.items[4].page_id = None
        self.items[4].talk_id = self.talk5.pk
        self.items[4].save()

        all_items = prefetch_schedule_items()
        self.assertEqual(list(find_speaker_clashes(all_items)), [])
        # Check two talks witht the same author at the same time fails
        self.items[1].talk_id = self.talk6.pk
        self.items[1].save()

        all_items = prefetch_schedule_items()
        result = list(find_speaker_clashes(all_items))
        self.assertEqual(len(result), 1)
        self.assertIn(self.author1, result[0][0])
        self.assertIn(self.slots[0], result[0][0])
        self.assertIn(self.items[0], result[0][1])
        self.assertIn(self.items[1], result[0][1])
        old_result = result

        # Check that it also fails if the one talk has multiple authors, and
        # the common speaker is not the primary author

        self.talk4.authors.add(self.author3)
        self.talk4.save()

        all_items = prefetch_schedule_items()
        result = list(find_speaker_clashes(all_items))

        self.assertEqual(len(result), 2)
        new_result = get_new_result(result, old_result)
        self.assertIn(self.author3, new_result[0][0])
        self.assertIn(self.slots[1], new_result[0][0])
        self.assertIn(self.items[2], new_result[0][1])
        self.assertIn(self.items[3], new_result[0][1])
        old_result = result

        # Check that it also fails if the speaker is assigned to a page and a talk

        self.pages[5].people.add(self.author5)
        self.pages[5].save()

        all_items = prefetch_schedule_items()
        result = list(find_speaker_clashes(all_items))

        self.assertEqual(len(result), 3)
        new_result = get_new_result(result, old_result)
        self.assertIn(self.author5, new_result[0][0])
        self.assertIn(self.slots[2], new_result[0][0])
        self.assertIn(self.items[4], new_result[0][1])
        self.assertIn(self.items[5], new_result[0][1])
        old_result = result

        # Check that it also fails in the case of 2 pages

        self.pages[6].people.add(self.author4)
        self.pages[6].people.add(self.author1)
        self.pages[6].save()

        self.pages[7].people.add(self.author4)
        self.pages[7].people.add(self.author3)
        self.pages[7].people.add(self.author2)
        self.pages[7].save()
        
        all_items = prefetch_schedule_items()
        result = list(find_speaker_clashes(all_items))

        self.assertEqual(len(result), 4)
        new_result = get_new_result(result, old_result)
        self.assertIn(self.author4, new_result[0][0])
        self.assertIn(self.slots[3], new_result[0][0])
        self.assertIn(self.items[6], new_result[0][1])
        self.assertIn(self.items[7], new_result[0][1])
        old_result = result

        # Also check that multiple clashing speakers are reported

        self.pages[6].people.add(self.author2)
        self.pages[6].save()

        all_items = prefetch_schedule_items()
        result = list(find_speaker_clashes(all_items))

        self.assertEqual(len(result), 5)
        new_result = get_new_result(result, old_result)
        self.assertIn(self.author2, new_result[0][0])
        self.assertIn(self.slots[3], new_result[0][0])
        self.assertIn(self.items[6], new_result[0][1])
        self.assertIn(self.items[7], new_result[0][1])
