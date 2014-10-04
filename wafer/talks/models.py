from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import models

from markitup.fields import MarkupField


# constants to make things clearer elsewhere
ACCEPTED = 'A'
PENDING = 'P'
REJECTED = 'R'


class TalkType(models.Model):
    """A type of talk."""
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=1024)

    def __unicode__(self):
        return u'%s' % (self.name,)


class Talk(models.Model):

    TALK_STATUS = (
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Not Accepted'),
        (PENDING, 'Under Consideration'),
    )

    talk_id = models.AutoField(primary_key=True)
    talk_type = models.ForeignKey(TalkType, null=True)

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
        settings.AUTH_USER_MODEL, related_name='contact_talks')
    authors = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                     related_name='talks')

    def __unicode__(self):
        return u'%s: %s' % (self.corresponding_author, self.title)

    def get_absolute_url(self):
        return reverse('wafer_talk', args=(self.talk_id,))

    def get_author_contact(self):
        email = self.corresponding_author.email
        profile = self.corresponding_author.get_profile()
        if profile.contact_number:
            contact = profile.contact_number
        else:
            # Should we wrap this in a span for styling?
            contact = 'NO CONTACT INFO'
        return '%s - %s' % (email, contact)
    get_author_contact.short_description = 'Contact Details'

    def get_author_name(self):
        return '%s (%s)' % (self.corresponding_author,
                            self.corresponding_author.get_full_name())

    get_author_name.admin_order_field = 'corresponding_author'
    get_author_name.short_description = 'Corresponding Author'

    def get_author_display_name(self):
        full_name = self.corresponding_author.get_full_name()
        if full_name:
            return full_name
        return self.corresponding_author.username

    def get_in_schedule(self):
        if self.scheduleitem_set.all():
            return True
        return False

    get_in_schedule.short_description = 'Added to schedule'
    get_in_schedule.boolean = True

    # Helpful properties for the templates
    accepted = property(fget=lambda x: x.status == ACCEPTED)
    pending = property(fget=lambda x: x.status == PENDING)
    reject = property(fget=lambda x: x.status == REJECTED)


class TalkUrl(models.Model):
    """An url to stuff relevant to the talk - videos, slides, etc.

       Note that these are explicitly not intended to be exposed to the
       user, but exist for use by the conference organisers."""

    description =  models.CharField(max_length=256)
    url = models.URLField()
    talk = models.ForeignKey(Talk)
