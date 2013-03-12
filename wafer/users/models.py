import os

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save


def photo_fn(instance, filename):
    '''Return the preferred filename for user photos'''
    ext = os.path.splitext(filename)[1]
    fn = ''.join((instance.user.username, ext))
    return os.path.join('users', fn)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    contact_number = models.CharField(max_length=16, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to=photo_fn, null=True, blank=True)

    homepage = models.CharField(max_length=256, null=True, blank=True)
    # We should probably do social auth instead
    # And care about other code hosting sites...
    twitter_handle = models.CharField(max_length=15, null=True, blank=True)
    github_username = models.CharField(max_length=32, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.user)

    def accepted_talks(self):
        return self.user.talks.filter(accepted=True)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
