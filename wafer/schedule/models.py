import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from wafer.pages.models import Page
from wafer.snippets.markdown_field import MarkdownTextField
from wafer.talks.models import Talk


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

    video = models.BooleanField(
        default=False,
        help_text=_("Venue has video coverage"))

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
                                      on_delete=models.CASCADE,
                                      help_text=_("Previous slot if "
                                                  "applicable (slots should "
                                                  "have either a previous "
                                                  "slot OR a day and start "
                                                  "time set)"))

    day = models.ForeignKey(Day, null=True, blank=True,
                            on_delete=models.PROTECT,
                            help_text=_("Day for this slot (if no "
                                        "previous slot selected)"))

    start_time = models.TimeField(null=True, blank=True,
                                  help_text=_("Start time (if no"
                                              " previous slot selected)"))
    end_time = models.TimeField(null=True, help_text=_("Slot end time"))

    name = models.CharField(max_length=1024, null=True, blank=True,
                            help_text=_("Identifier for use in the admin"
                                        " panel"))

    class Meta:
        ordering = ['day', 'end_time', 'start_time']

    def __str__(self):
        if self.name:
            slot = u'Slot %s' % self.name
        else:
            slot = u'Slot'
        start = self.get_formatted_start_time()
        end = self.get_formatted_end_time()
        return u'%s: %s: %s - %s' % (slot, self.get_day(), start, end)

    def get_start_time(self):
        if self.previous_slot:
            return self.previous_slot.end_time
        return self.start_time

    def get_formatted_start_time(self):
        return self.get_start_time().strftime('%H:%M')
    get_formatted_start_time.short_description = 'Start Time'

    def get_formatted_end_time(self):
        return self.end_time.strftime('%H:%M')

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

    def get_start_datetime(self):
        return datetime.datetime.combine(self.get_day().date,
                                         self.get_start_time())

    def get_end_datetime(self):
        return datetime.datetime.combine(self.get_day().date,
                                         self.end_time)

    def get_day(self):
        if self.previous_slot:
            return self.previous_slot.get_day()
        return self.day
    get_day.short_description = 'Day'

    def clean(self):
        """Ensure we have start_time < end_time"""
        if not self.previous_slot and not self.start_time:
            raise ValidationError("Slots must have a start time"
                                  " or previous slot set")
        if self.end_time and self.get_start_time() >= self.end_time:
            raise ValidationError("Start time must be before end time")
        # Slots should either have day + start_time, or a previous_slot, but
        # not both (since previous_slot overrides the others)
        if (self.day or self.start_time) and self.previous_slot:
            raise ValidationError("Slots with a previous slot should not "
                                  "have a day or start_time set")


@python_2_unicode_compatible
class ScheduleItem(models.Model):

    venue = models.ForeignKey(Venue,
                              on_delete=models.PROTECT)

    # Items can span multiple slots (tutorials, etc).
    slots = models.ManyToManyField(Slot)

    talk = models.ForeignKey(
        Talk, null=True, blank=True, on_delete=models.CASCADE)
    page = models.ForeignKey(
        Page, null=True, blank=True, on_delete=models.CASCADE)
    details = MarkdownTextField(
        null=False, blank=True,
        help_text=_("Additional details (if required)"))

    notes = models.TextField(
        null=False, blank=True,
        help_text=_("Notes for the conference organisers"))

    css_class = models.CharField(
        max_length=128, null=False, blank=True,
        help_text=_("Custom css class for this schedule item"))

    expand = models.BooleanField(
        null=False, default=False,
        help_text=_("Expand to neighbouring venues"))

    last_updated = models.DateTimeField(null=True, blank=True,
                                        auto_now=True,
                                        help_text=_("Date & Time this was"
                                                    " last updated"))

    def get_title(self):
        if self.talk:
            return self.talk.title
        elif self.page:
            return self.page.name
        elif self.details:
            return self.details
        return 'No title'

    def get_css_classes(self):
        """Get all applied CSS classes, based on this item, type, and track"""
        if self.css_class:
            yield self.css_class
        else:
            yield 'schedule'

        if self.talk:
            if self.talk.talk_type:
                yield self.talk.talk_type.css_class()
            if self.talk.track:
                yield self.talk.track.css_class()

    get_css_classes.short_description = 'Talk Type & Track CSS classes'

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

    def get_start_datetime(self):
        slots = list(self.slots.all())
        if slots:
            return slots[0].get_start_datetime()
        else:
            return None

    def get_start_time(self):
        slots = list(self.slots.all())
        if slots:
            start = slots[0].get_formatted_start_time()
            day = slots[0].get_day()
            return u'%s, %s' % (day, start)
        else:
            return 'WARNING: No Time and Day Specified'
    get_start_time.short_description = 'Start Time'

    def __str__(self):
        return u'%s in %s at %s' % (self.get_desc(), self.venue,
                                    self.get_start_time())

    def get_duration(self):
        """Return the total duration of the item.

           This is the sum of all the slot durations."""
        # This is intended for the pentabarf xml file
        # It will do the wrong thing if the slots aren't
        # contigious, which we should address sometime.
        slots = list(self.slots.all())
        result = {'hours': 0, 'minutes': 0}
        if slots:
            for slot in slots:
                dur = slot.get_duration()
                result['hours'] += dur['hours']
                result['minutes'] += dur['minutes']
            # Normalise again
            hours, result['minutes'] = divmod(result['minutes'], 60)
            result['hours'] += hours
        return result

    def get_duration_minutes(self):
        """Return the duration in total number of minutes."""
        duration = self.get_duration()
        return int(duration['hours'] * 60 + duration['minutes'])


def invalidate_check_schedule(*args, **kw):
    sender = kw.pop('sender', None)
    if sender is Talk or sender is Page:
        # For talks and pages, we only invalidate the schedule cache
        # if they in the schedule
        instance = kw.pop('instance')
        if not instance.get_in_schedule():
            return
    from wafer.schedule.admin import check_schedule
    check_schedule.invalidate()


def update_schedule_items(*args, **kw):
    """We save all the schedule items associated with this slot, so
       the last_update time is updated to reflect any changes to the
       timing of the slots"""
    slot = kw.pop('instance', None)
    if not slot:
        return
    for item in slot.scheduleitem_set.all():
        item.save(update_fields=['last_updated'])
    # We also need to update the next slot, in case we changed it's
    # times as well
    next_slot = slot.slot_set.all()
    if next_slot.count():
        # From the way we structure the slot tree, we know that
        # there's only 1 next slot that could have changed.
        for item in next_slot[0].scheduleitem_set.all():
            item.save(update_fields=['last_updated'])


post_save.connect(invalidate_check_schedule, sender=Day)
post_save.connect(invalidate_check_schedule, sender=Venue)
post_save.connect(invalidate_check_schedule, sender=Slot)
post_save.connect(invalidate_check_schedule, sender=ScheduleItem)

post_delete.connect(invalidate_check_schedule, sender=Day)
post_delete.connect(invalidate_check_schedule, sender=Venue)
post_delete.connect(invalidate_check_schedule, sender=Slot)
post_delete.connect(invalidate_check_schedule, sender=ScheduleItem)

# We also hook up calls from Page and Talk, so
# changes to those reflect in the schedule immediately
# We don't hook up the delete signals, because the deletion
# of the related ScheduleItem will do the right thing
# if they are in the schedule
post_save.connect(invalidate_check_schedule, sender=Talk)
post_save.connect(invalidate_check_schedule, sender=Page)

# Hook up post save connection between slots and schedule items
post_save.connect(update_schedule_items, sender=Slot)
