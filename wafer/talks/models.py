from django.db import models
from django.contrib.auth.models import User


class Talk(models.Model):

    talk_id = models.IntegerField(primary_key=True)

    title = models.CharField(max_length=1024)

    abstract = models.TextField()

    finalised = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)

    corresponding_author = models.ForeignKey(User,
            related_name='contact_talks')
    authors = models.ManyToManyField(User)
