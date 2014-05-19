from django.contrib import admin
from django import forms

from wafer.schedule.models import Venue, Slot, ScheduleItem
from wafer.talks.models import Talk, ACCEPTED
from wafer.pages.models import Page


# These are functions to simplify testing
def find_overlapping_slots():
    """Find any slots that overlap"""
    overlaps = set([])
    for slot in Slot.objects.all():
        # Because slots are ordered, we can be more efficient than this
        # N^2 loop, but this is simple and, since the number of slots
        # should be low, this should be "fast enough"
        start = slot.get_start_time()
        end = slot.end_time
        for other_slot in Slot.objects.all():
            if other_slot.pk == slot.pk:
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


def validate_items():
    """Find errors in the schedule. Check for:
         - pending / rejected talks in the schedule
         - items with both talks and pages assigned
         - items with neither talks nor pages assigned
         """
    validation = []
    for item in ScheduleItem.objects.all():
        if item.talk is not None and item.page is not None:
            validation.append(item)
        elif item.talk is None and item.page is None:
            validation.append(item)
        elif item.talk and item.talk.status != ACCEPTED:
            validation.append(item)
    return validation


def find_duplicate_schedule_items():
    """Find talks / pages assigned to mulitple schedule items"""
    duplicates = []
    seen_talks = {}
    seen_pages = {}
    for item in ScheduleItem.objects.all():
        if item.talk and item.talk in seen_talks:
            duplicates.append(item)
            if seen_talks[item.talk] not in duplicates:
                duplicates.append(seen_talks[item.talk])
        else:
            seen_talks[item.talk] = item
        if item.page and item.page in seen_pages:
            duplicates.append(item)
            if seen_pages[item.page] not in duplicates:
                duplicates.append(seen_pages[item.page])
        else:
            seen_pages[item.page] = item
    return duplicates


def find_clashes():
    """Find schedule items which clash (common slot and venue)"""
    clashes = {}
    seen_venue_slots = {}
    for item in ScheduleItem.objects.all():
        for slot in item.slots.all():
            pos = (item.venue, slot)
            if pos in seen_venue_slots:
                if seen_venue_slots[pos] not in clashes:
                    clashes[pos] = [seen_venue_slots[pos]]
                clashes[pos].append(item)
            else:
                seen_venue_slots[pos] = item
    return clashes


def check_schedule():
    """Helper routine to eaily test if the schedule is valid"""
    if find_clashes():
        return False
    if find_duplicate_schedule_items():
        return False
    if validate_items():
        return False
    if find_overlapping_slots():
        return False
    return True


class ScheduleItemAdminForm(forms.ModelForm):
    class Meta:
        model = ScheduleItem

    def __init__(self, *args, **kwargs):
        super(ScheduleItemAdminForm, self).__init__(*args, **kwargs)
        self.fields['talk'].queryset = Talk.objects.filter(status=ACCEPTED)
        # Present all pages as possible entries in the schedule
        self.fields['page'].queryset = Page.objects.all()


class ScheduleItemAdmin(admin.ModelAdmin):
    form = ScheduleItemAdminForm

    change_list_template = 'admin/scheduleitem_list.html'

    # We stuff these validation results into the view, rather than
    # enforcing conditions on the actual model, since it can be hard
    # to edit the schedule and keep it entirely consistent at every
    # step (think exchanging talks and so forth)
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Find issues in the schedule
        clashes = find_clashes()
        validation = validate_items()
        duplicates = find_duplicate_schedule_items()
        errors = {}
        if clashes:
            errors['clashes'] = clashes
        if duplicates:
            errors['duplicates'] = duplicates
        if validation:
            errors['validation'] = validation
        extra_context['errors'] = errors
        return super(ScheduleItemAdmin, self).changelist_view(request,
                                                              extra_context)


class SlotAdminForm(forms.ModelForm):
    class Meta:
        model = Slot

    class Media:
        js = ('js/scheduledatetime.js',)


class SlotAdmin(admin.ModelAdmin):
    form = SlotAdminForm

    list_display = ('__unicode__', 'end_time')
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


admin.site.register(Slot, SlotAdmin)
admin.site.register(Venue)
admin.site.register(ScheduleItem, ScheduleItemAdmin)
