from datetime import timedelta
from django.utils import timezone

from django.test import TestCase

from wafer.talks.models import TalkType


class TestTalkTypes(TestCase):
    """Collection of tests for talk type handling."""

    def test_open_by_default(self):
        """Check that types are open for submission by default"""
        talk_type = TalkType.objects.create()
        self.assertTrue(talk_type in TalkType.objects.open_for_submission())

    def test_closed_when_flagged_as_such(self):
        """Check that the closed submission  flag works"""
        talk_type = TalkType.objects.create(disable_submission=True)
        self.assertTrue(talk_type not in TalkType.objects.open_for_submission())

    def test_open_for_submission_by_date(self):
        """Check taht we can use dates to manage open/ closed state"""
        now = timezone.now()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=2)

        closed_talk_type = TalkType.objects.create(submission_deadline=yesterday)
        open_talk_type = TalkType.objects.create(submission_deadline=tomorrow)
        disabled_talk_type = TalkType.objects.create(
            submission_deadline=tomorrow,
            disable_submission=True,
        )

        self.assertTrue(open_talk_type in TalkType.objects.open_for_submission())
        self.assertTrue(closed_talk_type not in TalkType.objects.open_for_submission())

    def test_open_for_late_submissions(self):
        """Check that types that allow late submissions stay open"""
        now = timezone.now()
        yesterday = now - timedelta(days=1)

        talk_type = TalkType.objects.create(
            submission_deadline=yesterday,
            accept_late_submissions=True,
        )
        self.assertTrue(talk_type in TalkType.objects.open_for_submission())
