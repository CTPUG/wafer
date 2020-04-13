from datetime import timedelta
from django.utils import timezone

from wafer.talks.models import TalkType


def test_open_by_default():
    talk_type = TalkType.objects.create()
    assert talk_type in TalkType.objects.open_for_submission()


def test_closed_when_flagged_as_such():
    talk_type = TalkType.objects.create(disable_submission=True)
    assert talk_type not in TalkType.objects.open_for_submission()


def test_open_for_submission_by_date():
    now = timezone.now()
    yesterday = now - timedelta(days=1)
    tomorrow = now + timedelta(days=2)

    closed_talk_type = TalkType.objects.create(submission_deadline=yesterday)
    open_talk_type = TalkType.objects.create(submission_deadline=tomorrow)
    disabled_talk_type = TalkType.objects.create(
        submission_deadline=tomorrow,
        disable_submission=True,
    )

    assert open_talk_type in TalkType.objects.open_for_submission()
    assert closed_talk_type not in TalkType.objects.open_for_submission()


def test_open_for_late_submissions():
    now = timezone.now()
    yesterday = now - timedelta(days=1)

    talk_type = TalkType.objects.create(
        submission_deadline=yesterday,
        accept_late_submissions=True,
    )
    assert talk_type in TalkType.objects.open_for_submission()
