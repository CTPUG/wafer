# This tests the very basic talk stuff, to ensure some levels of sanity


def test_add_talk():
    """Create a user and add a talk to it"""
    from django.contrib.auth import get_user_model
    from wafer.talks.models import Talk

    user = get_user_model().objects.create_user('john', 'best@wafer.test',
                                                'johnpassword')
    Talk.objects.create(
        title="This is a test talk",
        abstract="This should be a long and interesting abstract, but isn't",
        corresponding_author_id=user.id)

    assert user.contact_talks.count() == 1


def test_filter_talk():
    """Create a second user and check some filters"""
    from django.contrib.auth import get_user_model

    UserModel = get_user_model()

    UserModel.objects.create_user('james', 'best@wafer.test', 'johnpassword')

    assert UserModel.objects.filter(contact_talks__isnull=False).count() == 1
    assert UserModel.objects.filter(contact_talks__isnull=True).count() == 1


def test_multiple_talks():
    """Add more talks"""
    from wafer.talks.models import Talk
    from django.contrib.auth import get_user_model

    UserModel = get_user_model()

    user1 = UserModel.objects.filter(username='john').get()
    user2 = UserModel.objects.filter(username='james').get()

    Talk.objects.create(
        title="This is a another test talk",
        abstract="This should be a long and interesting abstract, but isn't",
        corresponding_author_id=user1.id)

    assert len([x.title for x in user1.contact_talks.all()]) == 2
    assert len([x.title for x in user2.contact_talks.all()]) == 0

    Talk.objects.create(
        title="This is a third test talk",
        abstract="This should be a long and interesting abstract, but isn't",
        corresponding_author_id=user2.id)

    assert len([x.title for x in user2.contact_talks.all()]) == 1


def test_corresponding_author_details():
    """Create a second user and check some filters"""
    from django.contrib.auth import get_user_model
    from wafer.talks.models import Talk

    UserModel = get_user_model()

    user = UserModel.objects.create_user('jeff', 'best@wafer.test',
                                         'johnpassword')
    profile = user.userprofile
    profile.contact_number = '77776'
    profile.save()

    speaker = UserModel.objects.create_user('bob', 'bob@wafer.test',
                                            'bobpassword')

    Talk.objects.create(
        title="This is a another test talk",
        abstract="This should be a long and interesting abstract, but isn't",
        corresponding_author_id=user.id)

    talk = user.contact_talks.all()[0]
    talk.authors.add(user)
    talk.authors.add(speaker)
    talk.save()

    assert talk.get_authors_display_name() == 'jeff & bob'
    assert talk.get_corresponding_author_contact() == 'best@wafer.test - 77776'
    assert talk.get_corresponding_author_name() == 'jeff (jeff)'

    speaker.first_name = 'Bob'
    speaker.last_name = 'Robert'
    speaker.save()

    assert talk.get_authors_display_name() == 'jeff & Bob Robert'


def test_is_late_submission_no_talk_type():
    from wafer.talks.models import Talk

    assert not Talk().is_late_submission


def test_is_late_submission_no_deadline():
    from django.utils.timezone import now
    from wafer.talks.models import Talk, TalkType

    talk_type = TalkType()
    talk = Talk(submission_time=now(), talk_type=talk_type)

    assert not talk.is_late_submission


def test_is_late_submission_not_late():
    from django.utils.timezone import datetime, utc
    from wafer.talks.models import Talk, TalkType

    deadline = datetime(2019, 11, 1, 0, 0, 0, 0, utc)
    before_deadline = datetime(2019, 10, 15, 0, 0, 0, 0, utc)

    talk_type = TalkType(submission_deadline=deadline)
    not_late = Talk(talk_type=talk_type, submission_time=before_deadline)
    assert not not_late.is_late_submission


def test_is_late_submission_late():
    from django.utils.timezone import datetime, utc
    from wafer.talks.models import Talk, TalkType

    deadline = datetime(2019, 11, 1, 0, 0, 0, 0, utc)
    after_deadline = datetime(2019, 11, 2, 0, 0, 0, 0, utc)

    talk_type = TalkType(submission_deadline=deadline)
    late = Talk(talk_type=talk_type, submission_time=after_deadline)
    assert late.is_late_submission
