from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import get_current_timezone, localtime
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.db import models

from wafer.snippets.markdown_field import MarkdownTextField

from wafer.talks.models import Talk
from wafer.pages.models import Page


class Venue(models.Model):
    """Information about a venue for conference events"""
    order = models.IntegerField(default=1)

    name = models.CharField(max_length=1024)

    notes = MarkdownTextField(
        null=False, blank=True,
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

    previous_slot = models.ForeignKey('self', null=True, blank=True,
                                      help_text=_("Previous slot"))
    start_time = models.DateTimeField(null=True, blank=True,
                                      help_text=_("Start time (if no"
                                                  " previous slot)"))
    # Should we rather specify slot length instead of end time?
    end_time = models.DateTimeField(null=True, help_text=_("Slot end time"))

    name = models.CharField(max_length=1024, null=True, blank=True,
                            help_text=_("Identifier for use in the admin"
                                        " panel"))

    class Meta:
        ordering = ['end_time', 'start_time']

    def __unicode__(self):
        if self.name:
            slot = u'Slot %s' % self.name
        else:
            slot = u'Slot'
        # Should we be doing this with datetime.utils.timezone.activate?
        # If so, where?
        start_time = localtime(self.get_start_time(), get_current_timezone())
        end_time = localtime(self.end_time, get_current_timezone())
        day = self.get_start_time().strftime('%b %d (%a)')
        start = start_time.strftime('%H:%M')
        end = end_time.strftime('%H:%M')
        return u'%s: %s: %s - %s' % (slot, day, start, end)

    def get_start_time(self):
        if self.previous_slot:
            return self.previous_slot.end_time
        return self.start_time

    def clean(self):
        """Ensure we start_time < end_time"""
        if not self.previous_slot and not self.start_time:
            raise ValidationError("Slots must have a start time"
                                  " or previous slot set")
        if self.get_start_time() >= self.end_time:
            raise ValidationError("Start time must be before end time")


class ScheduleItem(models.Model):

    venue = models.ForeignKey(Venue)

    # Items can span multiple slots (tutorials, etc).
    slots = models.ManyToManyField(Slot)

    talk = models.ForeignKey(Talk, null=True, blank=True)
    page = models.ForeignKey(Page, null=True, blank=True)
    details = MarkdownTextField(
        null=False, blank=True,
        help_text=_("Additional details (if required)"))

    notes = models.TextField(
        null=False, blank=True,
        help_text=_("Notes for the conference organisers"))

    def get_title(self):
        if self.talk:
            return self.talk.title
        elif self.page:
            return self.page.name
        elif self.details:
            return self.details
        return 'No title'

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

    def get_start_time(self):
        start_time = localtime(list(self.slots.all())[0].get_start_time(),
                               get_current_timezone())
        day = start_time.strftime('%b %d (%a)')
        start = start_time.strftime('%H:%M')
        return u'%s, %s' % (day, start)

    def __unicode__(self):
        return u'%s in %s at %s' % (self.get_desc(), self.venue,
                                    self.get_start_time())
