from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from libravatar import libravatar_url
from urllib2 import urlparse

from wafer.talks.models import ACCEPTED, PENDING


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    contact_number = models.CharField(max_length=16, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    homepage = models.CharField(max_length=256, null=True, blank=True)
    # We should probably do social auth instead
    # And care about other code hosting sites...
    twitter_handle = models.CharField(max_length=15, null=True, blank=True)
    github_username = models.CharField(max_length=32, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.user)

    def accepted_talks(self):
        return self.user.talks.filter(status=ACCEPTED)

    def pending_talks(self):
        return self.user.talks.filter(status=PENDING)

    def manages_registration(self):
        return self.user.created.count() > 0

    def registrations(self):
        return self.user.created.all()

    def avatar_url(self, size=96, https=True, default='mm'):
        if not self.user.email:
            return None
        return libravatar_url(self.user.email, size=size, https=https,
                              default=default)

    def homepage_url(self):
        """Try ensure we prepend http: to the url if there's nothing there

           This is to ensure we're not generating relative links in the
           user templates."""
        if not self.homepage:
            return self.homepage
        parsed = urlparse.urlparse(self.homepage)
        if parsed.scheme:
            return self.homepage
        # Vague sanity check
        abs_url = ''.join(['http://', self.homepage])
        if urlparse.urlparse(abs_url).scheme == 'http':
            return abs_url
        return self.homepage


def create_user_profile(sender, instance, created, raw=False, **kwargs):
    if raw:
        return
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
