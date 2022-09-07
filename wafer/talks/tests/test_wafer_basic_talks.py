# This tests the very basic talk stuff, to ensure some levels of sanity

from datetime import timezone

from django.contrib.auth import get_user_model
from django.utils.timezone import datetime, now

from django.test import TestCase

from wafer.talks.models import Talk, TalkType, SUBMITTED
from wafer.talks.tests.fixtures import create_talk
from wafer.tests.utils import create_user


class TestBasicTalks(TestCase):
    """Basic talk tests"""

    def setUp(self):
        """Setup a user with a talk"""
        self.user = create_user('john')
        create_talk('This is a test talk', status=SUBMITTED, user=self.user)

    def test_add_talk(self):
        """Check that the created talk is found via the user"""
        self.assertTrue(self.user.contact_talks.count() == 1)

    def test_filter_talk(self):
        """Create a second user and check some filters"""
        create_user('james')

        UserModel = get_user_model()
        self.assertTrue(UserModel.objects.filter(contact_talks__isnull=False).count() == 1)
        self.assertTrue(UserModel.objects.filter(contact_talks__isnull=True).count() == 1)

    def test_multiple_talks(self):
        """Add more talks"""
        user2 = create_user('james')

        create_talk('This is a another test talk', status=SUBMITTED, user=self.user)

        self.assertTrue(len([x.title for x in self.user.contact_talks.all()]) == 2)
        self.assertTrue(len([x.title for x in user2.contact_talks.all()]) == 0)

        create_talk('This is a third test talk', status=SUBMITTED, user=user2)

        self.assertTrue(len([x.title for x in user2.contact_talks.all()]) == 1)


    def test_corresponding_author_details(self):
        """Create a second user and check some filters"""
        user = create_user('jeff')
        profile = user.userprofile
        profile.contact_number = '77776'
        profile.save()

        speaker = create_user('bob')

        create_talk('This is a another test talk', status=SUBMITTED, user=user)

        talk = user.contact_talks.all()[0]
        talk.authors.add(user)
        talk.authors.add(speaker)
        talk.save()

        self.assertTrue(talk.get_authors_display_name() == 'jeff & bob')
        self.assertTrue(talk.get_corresponding_author_contact() == 'jeff@example.com - 77776')
        self.assertTrue(talk.get_corresponding_author_name() == 'jeff (jeff)')

        speaker.first_name = 'Bob'
        speaker.last_name = 'Robert'
        speaker.save()

        self.assertTrue(talk.get_authors_display_name() == 'jeff & Bob Robert')


    def test_is_late_submission_no_talk_type(self):
        self.assertTrue(not Talk().is_late_submission)


    def test_is_late_submission_no_deadline(self):
        talk_type = TalkType()
        talk = Talk(submission_time=now(), talk_type=talk_type)

        self.assertTrue(not talk.is_late_submission)


    def test_is_late_submission_not_late(self):
        deadline = datetime(2019, 11, 1, 0, 0, 0, 0, timezone.utc)
        before_deadline = datetime(2019, 10, 15, 0, 0, 0, 0, timezone.utc)

        talk_type = TalkType(submission_deadline=deadline)
        not_late = Talk(talk_type=talk_type, submission_time=before_deadline)
        self.assertTrue(not not_late.is_late_submission)


    def test_is_late_submission_late(self):
        deadline = datetime(2019, 11, 1, 0, 0, 0, 0, timezone.utc)
        after_deadline = datetime(2019, 11, 2, 0, 0, 0, 0, timezone.utc)

        talk_type = TalkType(submission_deadline=deadline)
        late = Talk(talk_type=talk_type, submission_time=after_deadline)
        self.assertTrue(late.is_late_submission)
