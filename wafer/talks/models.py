import re
import json
from uuid import uuid4

import requests

from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.sites.models import get_current_site
from django.core.files.base import ContentFile
from django.contrib.auth.models import User

from wafer.utils import normalize_unicode
from wafer import constants


class Talks(models.Model):

    talk_id = models.IntegerField(primary_key=True)

    title = models.CharField(max_length=1024)

    abstract = models.TextField()

    finalised = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)

    corresponding_author = models.ForeignKey(User,
            related_name='contact_talks')
    authors = models.ManyToManyField(User)
