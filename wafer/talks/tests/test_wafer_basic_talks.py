# This tests the very basic talk stuff, to ensure some levels of sanity


def test_add_talk():
    """Create a user and add a talk to it"""
    from django.contrib.auth.models import User
    from wafer.talks.models import Talk

    user = User.objects.create_user('john', 'best@wafer.test', 'johnpassword')
    Talk.objects.create(
        title="This is a test talk",
        abstract="This should be a long and interesting abstract, but isn't",
        corresponding_author_id=user.id)

    assert user.contact_talks.count() == 1


def test_filter_talk():
    """Create a second user and check some filters"""
    from django.contrib.auth.models import User

    User.objects.create_user('james', 'best@wafer.test', 'johnpassword')

    assert User.objects.filter(contact_talks__isnull=False).count() == 1
    assert User.objects.filter(contact_talks__isnull=True).count() == 1


def test_multiple_talks():
    """Add more talks"""
    from wafer.talks.models import Talk
    from django.contrib.auth.models import User

    user1 = User.objects.filter(username='john').get()
    user2 = User.objects.filter(username='james').get()

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
