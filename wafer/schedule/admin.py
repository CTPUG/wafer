import datetime

from django.contrib import admin
from django.contrib import messages
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _
from django import forms

from wafer.schedule.models import Day, Venue, Slot, ScheduleItem
from wafer.talks.models import Talk, ACCEPTED
from wafer.pages.models import Page
from wafer.utils import cache_result


# These are functions to simplify testing
def find_overlapping_slots():
    """Find any slots that overlap"""
    overlaps = set([])
    all_slots = list(Slot.objects.all())
    for slot in all_slots:
        # Because slots are ordered, we can be more efficient than this
        # N^2 loop, but this is simple and, since the number of slots
        # should be low, this should be "fast enough"
        start = slot.get_start_time()
        end = slot.end_time
        for other_slot in all_slots:
            if other_slot.pk == slot.pk:
                continue
            if other_slot.get_day() != slot.get_day():
                # different days, can't overlap
                continue
            # Overlap if the start_time or end_time is bounded by our times
            # start_time <= other.start_time < end_time
            # or
            # start_time < other.end_time <= end_time
            other_start = other_slot.get_start_time()
            other_end = other_slot.end_time
            if start <= other_start and other_start < end:
                overlaps.add(slot)
                overlaps.add(other_slot)
            elif start < other_end and other_end <= end:
                overlaps.add(slot)
                overlaps.add(other_slot)
    return overlaps


def validate_items(all_items=None):
    """Find errors in the schedule. Check for:
         - pending / rejected talks in the schedule
         - items with both talks and pages assigned
         - items with neither talks nor pages assigned
         """
    if all_items is None:
        all_items = prefetch_schedule_items()
    validation = []
    for item in all_items:
        if item.talk is not None and item.page is not None:
            validation.append(item)
        elif item.talk is None and item.page is None:
            validation.append(item)
        elif item.talk and item.talk.status != ACCEPTED:
            validation.append(item)
    return validation


def find_duplicate_schedule_items(all_items=None):
    """Find talks / pages assigned to mulitple schedule items"""
    if all_items is None:
        all_items = prefetch_schedule_items()
    duplicates = []
    seen_talks = {}
    for item in all_items:
        if item.talk and item.talk in seen_talks:
            duplicates.append(item)
            if seen_talks[item.talk] not in duplicates:
                duplicates.append(seen_talks[item.talk])
        else:
            seen_talks[item.talk] = item
        # We currently allow duplicate pages for cases were we need disjoint
        # schedule items, like multiple open space sessions on different
        # days and similar cases. This may be revisited later
    return duplicates


def find_clashes(all_items=None):
    """Find schedule items which clash (common slot and venue)"""
    if all_items is None:
        all_items = prefetch_schedule_items()
    clashes = {}
    seen_venue_slots = {}
    for item in all_items:
        for slot in item.slots.all():
            pos = (item.venue, slot)
            if pos in seen_venue_slots:
                if seen_venue_slots[pos] not in clashes:
                    clashes[pos] = [seen_venue_slots[pos]]
                clashes[pos].append(item)
            else:
                seen_venue_slots[pos] = item
    return clashes


def find_invalid_venues(all_items=None):
    """Find venues assigned slots that aren't on the allowed list
       of days."""
    if all_items is None:
        all_items = prefetch_schedule_items()
    venues = {}
    for item in all_items:
        valid = False
        item_days = list(item.venue.days.all())
        for slot in item.slots.all():
            for day in item_days:
                if day == slot.get_day():
                    valid = True
                    break
        if not valid:
            venues.setdefault(item.venue, [])
            venues[item.venue].append(item)
    return venues


def prefetch_schedule_items():
    """Prefetch all schedule items and related objects."""
    return list(ScheduleItem.objects
                .select_related(
                    'talk', 'page', 'venue')
                .prefetch_related(
                    'slots', 'slots__previous_slot', 'slots__day')
                .all())


@cache_result('wafer_schedule_check_schedule', 60*60)
def check_schedule():
    """Helper routine to eaily test if the schedule is valid"""
    all_items = prefetch_schedule_items()
    if find_clashes(all_items):
        return False
    if find_duplicate_schedule_items(all_items):
        return False
    if validate_items(all_items):
        return False
    if find_overlapping_slots():
        return False
    if find_invalid_venues(all_items):
        return False
    return True


class ScheduleItemAdminForm(forms.ModelForm):
    class Meta:
        model = ScheduleItem
        fields = ('slots', 'venue', 'talk', 'page', 'details', 'notes',
                  'css_class')

    def __init__(self, *args, **kwargs):
        super(ScheduleItemAdminForm, self).__init__(*args, **kwargs)
        self.fields['talk'].queryset = Talk.objects.filter(status=ACCEPTED)
        # Present all pages as possible entries in the schedule
        self.fields['page'].queryset = Page.objects.all()


class ScheduleItemAdmin(admin.ModelAdmin):
    form = ScheduleItemAdminForm

    change_list_template = 'admin/scheduleitem_list.html'
    list_display = ['get_start_time', 'venue', 'get_title']

    # We stuff these validation results into the view, rather than
    # enforcing conditions on the actual model, since it can be hard
    # to edit the schedule and keep it entirely consistent at every
    # step (think exchanging talks and so forth)
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Find issues in the schedule
        clashes = find_clashes()
        validation = validate_items()
        venues = find_invalid_venues()
        duplicates = find_duplicate_schedule_items()
        errors = {}
        if clashes:
            errors['clashes'] = clashes
        if duplicates:
            errors['duplicates'] = duplicates
        if validation:
            errors['validation'] = validation
        if venues:
            errors['venues'] = venues
        extra_context['errors'] = errors
        return super(ScheduleItemAdmin, self).changelist_view(request,
                                                              extra_context)


class SlotAdminForm(forms.ModelForm):

    class Meta:
        model = Slot
        fields = ('name', 'previous_slot', 'day', 'start_time', 'end_time')

    class Media:
        js = ('js/scheduledatetime.js',)


class SlotAdminAddForm(SlotAdminForm):

    # Additional field added for creating multiple slots at once
    additional = forms.IntegerField(min_value=0, max_value=30, required=False,
                                    label=_("Additional slots"),
                                    help_text=_("Create this number of "
                                                "additional slots following"
                                                "this one"))


class SlotAdmin(admin.ModelAdmin):
    form = SlotAdminForm

    list_display = ('__str__', 'day', 'end_time')
    list_editable = ('end_time',)

    change_list_template = 'admin/slot_list.html'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Find issues with the slots
        errors = {}
        overlaps = find_overlapping_slots()
        if overlaps:
            errors['overlaps'] = overlaps
        extra_context['errors'] = errors
        return super(SlotAdmin, self).changelist_view(request,
                                                      extra_context)

    def get_form(self, request, obj=None, **kwargs):
        """Change the form depending on whether we're adding or
           editing the slot."""
        if obj is None:
            # Adding a new Slot
            kwargs['form'] = SlotAdminAddForm
        return super(SlotAdmin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        super(SlotAdmin, self).save_model(request, obj, form, change)
        if not change and form.cleaned_data['additional'] > 0:
            # We add the requested additional slots
            # All created slot will have the same length as the slot just
            # created , and we specify them as a sequence using
            # "previous_slot" so tweaking start times is simple.
            prev = obj
            end = datetime.datetime.combine(prev.day.date, prev.end_time)
            start = datetime.datetime.combine(prev.day.date,
                                              prev.get_start_time())
            slot_len = end - start
            for loop in range(form.cleaned_data['additional']):
                end = end + slot_len
                new_slot = Slot(day=prev.day, previous_slot=prev,
                                end_time=end.time())
                new_slot.save()
                msgdict = {'obj': force_text(new_slot)}
                msg = _("Additional slot %(obj)s added sucessfully") % msgdict
                if hasattr(request, '_messages'):
                    # Don't add messages unless we have a suitable request
                    # Needed during testing, and possibly in other cases
                    self.message_user(request, msg, messages.SUCCESS)
                prev = new_slot


admin.site.register(Day)
admin.site.register(Slot, SlotAdmin)
admin.site.register(Venue)
admin.site.register(ScheduleItem, ScheduleItemAdmin)
