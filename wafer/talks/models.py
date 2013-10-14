from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models

from markitup.fields import MarkupField


# constants to make things clearer elsewhere
ACCEPTED = 'A'
PENDING = 'P'
REJECTED = 'R'


class Talk(models.Model):

    TALK_STATUS = (
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Not Accepted'),
        (PENDING, 'Under Consideration'),
    )

    talk_id = models.AutoField(primary_key=True)

    title = models.CharField(max_length=1024)

    abstract = MarkupField(
        help_text=_("Write two or three paragraphs describing your talk. "
                    "Who is your audience? What will they get out of it? "
                    "What will you cover?<br />"
                    "You can use Markdown syntax."))
    notes = models.TextField(
        null=True, blank=True,
        help_text=_("Any notes for the conference organisers?"))

    status = models.CharField(max_length=1, choices=TALK_STATUS,
                              default=PENDING)

    corresponding_author = models.ForeignKey(
        User, related_name='contact_talks')
    authors = models.ManyToManyField(User, related_name='talks')

    def __unicode__(self):
        return u'%s: %s' % (self.corresponding_author, self.title)

    def get_absolute_url(self):
        return reverse('wafer_talk', args=(self.talk_id,))

    # Helpful properties for the templates
    accepted = property(fget=lambda x: x.status == ACCEPTED)
    pending = property(fget=lambda x: x.status == PENDING)
    reject = property(fget=lambda x: x.status == REJECTED)
