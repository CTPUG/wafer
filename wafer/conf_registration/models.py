from django.contrib.auth.models import User
from django.db import models


class ConferenceOptionGroup(models.Model):
    """Used to manage relationships"""
    name = models.CharField(max_length=255)


class ConferenceOption(models.Model):

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    groups = models.ManyToManyField(
            ConferenceOptionGroup, related_name='members')
    requirements = models.ManyToManyField(
            ConferenceOptionGroup, related_name='enables')


class RegisteredAttendee(models.Model):

    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    items = models.ManyToManyField(
            ConferenceOption, related_name='attendees')
    registered_by = models.ForeignKey(
            User, related_name='registerations')
