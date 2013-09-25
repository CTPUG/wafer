from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.db import models

from wafer.snippets.markdown_field import MarkdownTextField

from wafer.talks.models import Talk
from wafer.pages.models import Page


class Venue(models.Model):
    """Information about a venue for conference events"""
    order = models.IntegerField(default=1)

    name = models.CharField(max_length=1024)

    notes = MarkdownTextField(
        help_text=_("Notes or directions that will be useful to"
                    " conference attendees"))

    class Meta:
        ordering = ['order', 'name']

    def __unicode__(self):
        return u'%s' % self.name

    def get_absolute_url(self):
        return reverse('wafer_venue', args=(self.pk,))


class Slot(models.Model):

    # XXX: We're trading flexibility for ease of implementation here.
    #      Revisit this when we have a better idea of the actual
    #      requirements.

    start_time = models.DateTimeField(null=True, blank=True)

    end_time = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return u'Slot: %s - %s' % (self.start_time.isoformat(),
                                   self.end_time.isoformat())


class ScheduleItem(models.Model):

    venue = models.ForeignKey(Venue)

    # Items can span multiple slots (tutorials, etc).
    slots = models.ManyToManyField(Slot)

    talk = models.ForeignKey(Talk, null=True)
    page = models.ForeignKey(Page, null=True)
    details = MarkdownTextField(
        null=False, blank=True,
        help_text=_("Additional details (if required)"))

    notes = models.TextField(
        null=False, blank=True,
        help_text=_("Notes for the conference organisers"))

    def get_desc(self):
        if self.details:
            if self.talk:
                return '%s - %s' % (self.talk.title, self.details)
            elif self.page:
                return '%s - %s' % (self.page.name, self.details)
            return self.details
        elif self.talk:
            return self.talk.title
        elif self.page:
            return self.page.name
        return ''

    def get_url(self):
        if self.talk:
            return self.talk.get_absolute_url()
        elif self.page:
            return self.page.get_absolute_url()
        return None

    def get_details(self):
        return self.get_desc()

    def __unicode__(self):
        return u'%s in %s' % (self.get_desc(), self.venue)
