from django.contrib import admin
from django import forms

from wafer.schedule.models import Venue, Slot, ScheduleItem
from wafer.talks.models import Talk, ACCEPTED
from wafer.pages.models import Page


# These are functions to simplify testing
def validate_slots():
    """Find any slots that overlap"""
    overlaps = []
    return overlaps


def validate_items():
    """Find errors in the schedule. Check for:
         - pending / rejected talks in the schedule
         - items with both talks and pages assigned
         """
    validation = []
    for item in ScheduleItem.objects.all():
        if item.talk is not None and item.page is not None:
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


class ScheduleItemAdminForm(forms.ModelForm):
    class Meta:
        model = ScheduleItem

    def __init__(self, *args, **kwargs):
        super(ScheduleItemAdminForm, self).__init__(*args, **kwargs)
        self.fields['talk'].queryset = Talk.objects.filter(status=ACCEPTED)
        # We assume items not in the menu aren't intended for the schedule
        # either - Is this the best assumption?
        self.fields['page'].queryset = Page.objects.filter(
            include_in_menu=True)


class ScheduleItemAdmin(admin.ModelAdmin):
    form = ScheduleItemAdminForm

    change_list_template = 'admin/scheduleitem_list.html'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        talks = [x for x in Talk.objects.filter(status=ACCEPTED)
                 if not x.scheduleitem_set.all()]
        extra_context['missed_talks'] = talks
        pages = [x for x in Page.objects.filter(include_in_menu=True)
                 if not x.scheduleitem_set.all()]
        extra_context['missed_pages'] = pages

        # errors are the following
        # Schedule items with both page and talk set
        # Same talk scheduled in multiple items
        # Same page scheduled in multiple items
        # Two schedule items with the same venue and at least 1 common slot
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


admin.site.register(Slot, SlotAdmin)
admin.site.register(Venue)
admin.site.register(ScheduleItem, ScheduleItemAdmin)
