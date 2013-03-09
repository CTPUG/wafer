import os

from django.contrib.auth.models import User
from django.db import models


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
