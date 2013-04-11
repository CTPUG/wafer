from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models


class ConferenceOptionGroup(models.Model):
    """Used to manage relationships"""
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return u'%s' % self.name


class ConferenceOption(models.Model):

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    groups = models.ManyToManyField(
            ConferenceOptionGroup, related_name='members',
            help_text='Groups this option belongs to.')
    requirements = models.ManyToManyField(
            ConferenceOptionGroup, related_name='enables',
            help_text='Option groups that this relies on',
            blank=True)

    def __unicode__(self):
        return u'%s (%.2f)' % (self.name, self.price)


class RegisteredAttendee(models.Model):

    class Meta:
        unique_together = (('name', 'email'))

    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    items = models.ManyToManyField(
            ConferenceOption, related_name='attendees')
    registered_by = models.ForeignKey(
            User, related_name='created')

    def get_absolute_url(self):
        return reverse('wafer_registration', args=(self.pk,))


    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.email)


