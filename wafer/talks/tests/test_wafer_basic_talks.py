# This tests the very basic talk stuff, to ensure some levels of sanity

from django.contrib.auth import get_user_model
from django.utils.timezone import datetime, now, utc

from wafer.talks.models import Talk, TalkType, SUBMITTED
from wafer.talks.tests.fixtures import create_talk
from wafer.tests.utils import create_user


def test_add_talk():
    """Create a user and add a talk to it"""
    user = create_user('john')
    create_talk('This is a test talk', status=SUBMITTED, user=user)

    assert user.contact_talks.count() == 1


def test_filter_talk():
    """Create a second user and check some filters"""
    create_user('james')

    UserModel = get_user_model()
    assert UserModel.objects.filter(contact_talks__isnull=False).count() == 1
    assert UserModel.objects.filter(contact_talks__isnull=True).count() == 1


def test_multiple_talks():
    """Add more talks"""
    UserModel = get_user_model()

    user1 = UserModel.objects.filter(username='john').get()
    user2 = UserModel.objects.filter(username='james').get()

    create_talk('This is a another test talk', status=SUBMITTED, user=user1)

    assert len([x.title for x in user1.contact_talks.all()]) == 2
    assert len([x.title for x in user2.contact_talks.all()]) == 0

    create_talk('This is a third test talk', status=SUBMITTED, user=user2)

    assert len([x.title for x in user2.contact_talks.all()]) == 1


def test_corresponding_author_details():
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

    assert talk.get_authors_display_name() == 'jeff & bob'
    assert talk.get_corresponding_author_contact() == 'jeff@example.com - 77776'
    assert talk.get_corresponding_author_name() == 'jeff (jeff)'

    speaker.first_name = 'Bob'
    speaker.last_name = 'Robert'
    speaker.save()

    assert talk.get_authors_display_name() == 'jeff & Bob Robert'


def test_is_late_submission_no_talk_type():
    assert not Talk().is_late_submission


def test_is_late_submission_no_deadline():
    talk_type = TalkType()
    talk = Talk(submission_time=now(), talk_type=talk_type)

    assert not talk.is_late_submission


def test_is_late_submission_not_late():
    deadline = datetime(2019, 11, 1, 0, 0, 0, 0, utc)
    before_deadline = datetime(2019, 10, 15, 0, 0, 0, 0, utc)

    talk_type = TalkType(submission_deadline=deadline)
    not_late = Talk(talk_type=talk_type, submission_time=before_deadline)
    assert not not_late.is_late_submission


def test_is_late_submission_late():
    deadline = datetime(2019, 11, 1, 0, 0, 0, 0, utc)
    after_deadline = datetime(2019, 11, 2, 0, 0, 0, 0, utc)

    talk_type = TalkType(submission_deadline=deadline)
    late = Talk(talk_type=talk_type, submission_time=after_deadline)
    assert late.is_late_submission
