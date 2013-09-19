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

    def __unicode__(self):
        return u'%s' % self.name

    def get_absolute_url(self):
        return reverse('wafer_venue', args=(self.pk,))


class ScheduleItem(models.Model):

    venue = models.ForeignKey(Venue)

    start_time = models.DateTimeField(null=True, blank=True)

    end_time = models.DateTimeField(null=True, blank=True)

    talk = models.ForeignKey(Talk, null=True)
    page = models.ForeignKey(Page, null=True)
    details = models.MarkdownTextField(
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

    def __unicode__(self):
        return u'%s in %s' % (self.get_desc(), self.venue)
