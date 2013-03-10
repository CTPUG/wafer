from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models


class Talk(models.Model):

    talk_id = models.IntegerField(primary_key=True)

    title = models.CharField(max_length=1024)

    abstract = models.TextField(
        help_text=_("Write two or three paragraphs describing your talk"))

    finalised = models.BooleanField(default=False,
        help_text=_("One way: You can't edit a finalised talk"))
    accepted = models.BooleanField(default=False)

    corresponding_author = models.ForeignKey(User,
        related_name='contact_talks')
    authors = models.ManyToManyField(User)

    def __unicode__(self):
        return u'%s: %s' % (self.corresponding_author, self.title)

    def get_absolute_url(self):
        return reverse('wafer_talk', args=(self.talk_id,))
