# This tests the very basic talk stuff, to ensure some levels of sanity


def test_add_talk():
   """Create a user and add a talk to it"""
   from django.contrib.auth.models import User
   from wafer.talks.models import Talks

   user = User.objects.create_user('john', 'best@wafer.test', 'johnpassword')
   talk = Talks.objects.create(title="This is a test talk",
         abstract="This should be a long and interesting abstract, but isn't",
         corresponding_author_id=user.id)

   assert user.contact_talks.count() == 1
