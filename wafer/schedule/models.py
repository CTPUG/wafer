import datetime

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.utils.encoding import python_2_unicode_compatible

from wafer.snippets.markdown_field import MarkdownTextField

from wafer.talks.models import Talk
from wafer.pages.models import Page


@python_2_unicode_compatible
class Day(models.Model):
    """Days on which the conference will be held."""
    date = models.DateField(null=True, blank=True)

    def __str__(self):
        return u'%s' % self.date.strftime('%b %d (%a)')

    class Meta:
        ordering = ['date']


@python_2_unicode_compatible
class Venue(models.Model):
    """Information about a venue for conference events"""
    order = models.IntegerField(default=1)

    name = models.CharField(max_length=1024)

    notes = MarkdownTextField(
        null=False, blank=True,
        help_text=_("Notes or directions that will be useful to"
                    " conference attendees"))

    days = models.ManyToManyField(Day, help_text=_("Days on which this venue"
                                                   " will be used."))

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return u'%s' % self.name

    def get_absolute_url(self):
        return reverse('wafer_venue', args=(self.pk,))


@python_2_unicode_compatible
class Slot(models.Model):

    # XXX: We're trading flexibility for ease of implementation here.
    #      Revisit this when we have a better idea of the actual
    #      requirements.

    previous_slot = models.ForeignKey('self', null=True, blank=True,
                                      help_text=_("Previous slot"))

    day = models.ForeignKey(Day, null=True, blank=True,
                            help_text=_("Day for this slot"))

    start_time = models.TimeField(null=True, blank=True,
                                  help_text=_("Start time (if no"
                                              " previous slot)"))
    end_time = models.TimeField(null=True, help_text=_("Slot end time"))

    name = models.CharField(max_length=1024, null=True, blank=True,
                            help_text=_("Identifier for use in the admin"
                                        " panel"))

    class Meta:
        order_with_respect_to = 'day'
        ordering = ['day', 'end_time', 'start_time']

    def __str__(self):
        if self.name:
            slot = u'Slot %s' % self.name
        else:
            slot = u'Slot'
        start = self.get_start_time().strftime('%H:%M')
        end = self.end_time.strftime('%H:%M')
        return u'%s: %s: %s - %s' % (slot, self.get_day(), start, end)

    def get_start_time(self):
        if self.previous_slot:
            return self.previous_slot.end_time
        return self.start_time

    def get_duration(self):
        """Return the duration of the slot as hours and minutes.

           Used for the pentabarf export, which needs it in this format."""
        start = datetime.datetime.combine(self.get_day().date,
                                          self.get_start_time())
        end = datetime.datetime.combine(self.get_day().date,
                                        self.end_time)
        duration = (end - start).total_seconds()
        result = {}
        result['hours'], result['minutes'] = divmod(duration // 60, 60)
        return result

    def get_day(self):
        if self.previous_slot:
            return self.previous_slot.get_day()
        return self.day

    def clean(self):
        """Ensure we have start_time < end_time"""
        if not self.previous_slot and not self.start_time:
            raise ValidationError("Slots must have a start time"
                                  " or previous slot set")
        if self.get_start_time() >= self.end_time:
            raise ValidationError("Start time must be before end time")


@python_2_unicode_compatible
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

    css_class = models.CharField(
        max_length=128, null=False, blank=True,
        help_text=_("Custom css class for this schedule item"))

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
        start_slot = list(self.slots.all())[0]
        start = start_slot.get_start_time().strftime('%H:%M')
        return u'%s, %s' % (start_slot.get_day(), start)

    def __str__(self):
        return u'%s in %s at %s' % (self.get_desc(), self.venue,
                                    self.get_start_time())


def invalidate_check_schedule(*args, **kw):
    from wafer.schedule.admin import check_schedule
    check_schedule.invalidate()


post_save.connect(invalidate_check_schedule, sender=Day)
post_save.connect(invalidate_check_schedule, sender=Venue)
post_save.connect(invalidate_check_schedule, sender=Slot)
post_save.connect(invalidate_check_schedule, sender=ScheduleItem)
