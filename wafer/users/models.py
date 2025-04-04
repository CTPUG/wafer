import logging

logger = logging.getLogger(__name__)

from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist

from libravatar import libravatar_url
try:
    from urllib2 import urlparse
except ImportError:
    from urllib import parse as urlparse

from wafer.kv.models import KeyValue
from wafer.talks.models import (ACCEPTED, SUBMITTED, UNDER_CONSIDERATION,
                                PROVISIONAL, CANCELLED)


PROFILE_GROUP = 'Online Profiles'


class UserProfile(models.Model):

    class Meta:
        ordering = ['id']
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    kv = models.ManyToManyField(KeyValue)
    contact_number = models.CharField(_('contact number'), max_length=16, null=True, blank=True)
    bio = models.TextField(_('bio'), null=True, blank=True)

    homepage = models.CharField(_('homepage'), max_length=256, null=True, blank=True)

    def __str__(self):
        return u'%s' % self.user

    def accepted_talks(self):
        return self.user.talks.filter(status=ACCEPTED)

    def provisional_talks(self):
        return self.user.talks.filter(status=PROVISIONAL)

    def pending_talks(self):
        return self.user.talks.filter(Q(status=SUBMITTED) |
                                      Q(status=UNDER_CONSIDERATION))

    def cancelled_talks(self):
        return self.user.talks.filter(status=CANCELLED)

    def published_talks(self):
        return self.user.talks.filter(status__in=(ACCEPTED, CANCELLED))

    def avatar_url(self, size=96, https=True, default='mm'):
        if not self.user.email:
            return None
        try:
            return libravatar_url(self.user.email, size=size, https=https,
                                  default=default)
        except UnicodeError as e:
            logger.error("Failed to determine libravatar URL for %s: %s",
                         self.user.email, e)

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

    def display_name(self):
        return self.user.get_full_name() or self.user.username

    def is_registered(self):
        is_registered = import_string(settings.WAFER_USER_IS_REGISTERED)
        return is_registered(self.user)

    def ticket_types(self):
        ticket_types = import_string(settings.WAFER_USER_TICKET_TYPES)
        return [x.name for x in ticket_types(self.user)]

    is_registered.boolean = True


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, raw=False, **kwargs):
    if raw:
        return
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def add_default_groups(sender, instance, created, raw=False, **kwargs):
    """Add the user to the configured set of default groups"""
    if raw:
        return
    if created:
        for grp_name in settings.WAFER_DEFAULT_GROUPS:
            try:
                group = Group.objects.get_by_natural_key(grp_name)
                instance.groups.add(group)
            except ObjectDoesNotExist:
                logger.warning("Specified default group %s not found" % grp_name)
