import datetime
from collections import defaultdict

from django.db.models import Q
from django.conf.urls import url
from django.core.exceptions import ValidationError

from django.contrib import admin
from django.contrib import messages
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _
from django import forms
from reversion.admin import VersionAdmin

from wafer.compare.admin import CompareVersionAdmin
from wafer.schedule.models import ScheduleBlock, Venue, Slot, ScheduleItem
from wafer.talks.models import Talk, ACCEPTED, CANCELLED
from wafer.pages.models import Page
from wafer.utils import cache_result


# Schedule item validators
def find_non_contiguous(all_items):
    """Find any items that have slots that aren't contiguous"""
    non_contiguous = []
    for item in all_items:
        if item.slots.count() < 2:
            # No point in checking
            continue
        last_slot = None
        for slot in item.slots.all().order_by('end_time'):
            if last_slot:
                if last_slot.end_time != slot.get_start_time():
                    non_contiguous.append(item)
                    break
            last_slot = slot
    return non_contiguous


def validate_items(all_items):
    """Find errors in the schedule. Check for:
         - pending / rejected talks in the schedule
         - items with both talks and pages assigned
         - items with neither talks nor pages assigned
         """
    validation = []
    for item in all_items:
        if item.talk is not None and item.page is not None:
            validation.append(item)
        elif item.talk is None and item.page is None:
            validation.append(item)
        elif item.talk and item.talk.status not in [ACCEPTED, CANCELLED]:
            validation.append(item)
    return validation


def find_duplicate_schedule_items(all_items):
    """Find talks / pages assigned to mulitple schedule items"""
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


def find_clashes(all_items):
    """Find schedule items which clash (common slot and venue)"""
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
    # We return a list, to match other validators
    return clashes.items()


def find_invalid_venues(all_items):
    """Find venues assigned slots that aren't on the allowed list
       of blocks."""
    venues = {}
    for item in all_items:
        valid = False
        item_blocks = list(item.venue.blocks.all())
        for slot in item.slots.all():
            for block in item_blocks:
                if block == slot.get_block():
                    valid = True
                    break
        if not valid:
            venues.setdefault(item.venue, [])
            venues[item.venue].append(item)
    return venues.items()


# Helper methods for calling the validators
def prefetch_schedule_items():
    """Prefetch all schedule items and related objects."""
    return list(ScheduleItem.objects
                .select_related(
                    'talk', 'page', 'venue')
                .prefetch_related(
                    'slots', 'slots__previous_slot')
                .all())


def prefetch_slots():
    return list(Slot.objects.all())


# Validators are listed as (function, error type, error message) tuples
SLOT_VALIDATORS = []
SCHEDULE_ITEM_VALIDATORS = []


# Helpers for people extending the tests
def register_slot_validator(function, err_type, msg):
    global SLOT_VALIDATORS
    SLOT_VALIDATORS.append((function, err_type, msg))


def register_schedule_item_validator(function, err_type, msg):
    global SCHEDULE_ITEM_VALIDATORS
    SCHEDULE_ITEM_VALIDATORS.append((function, err_type, msg))


# Register our validators
register_schedule_item_validator(
        find_clashes, 'clashes',
        _('Clashes found in schedule.'))
register_schedule_item_validator(
        find_duplicate_schedule_items, 'duplicates',
        _('Duplicate schedule items found in schedule.'))
register_schedule_item_validator(
        validate_items, 'validation',
        _('Invalid schedule items found in schedule.'))
register_schedule_item_validator(
        find_non_contiguous, 'non_contiguous',
        _('Non contiguous slots found in schedule.'))
register_schedule_item_validator(
        find_invalid_venues, 'venues',
        _('Invalid venues found in schedule.'))


# Utility functions for checking the schedule state
@cache_result('wafer_schedule_check_schedule', 60*60)
def check_schedule():
    """Helper routine to easily test if the schedule is valid"""
    all_items = prefetch_schedule_items()
    for validator, _type, _msg in SCHEDULE_ITEM_VALIDATORS:
        if validator(all_items):
            return False

    all_slots = prefetch_slots()
    for validator, _type, _msg in SLOT_VALIDATORS:
        if validator(all_slots):
            return False
    return True


def validate_schedule():
    """Helper routine to report issues with the schedule"""
    all_items = prefetch_schedule_items()
    errors = []
    for validator, _type, msg in SCHEDULE_ITEM_VALIDATORS:
        for item in validator(all_items):
            errors.append('%s: %s' % (msg, item))

    all_slots = prefetch_slots()
    for validator, _type, msg in SLOT_VALIDATORS:
        for slot in validator(all_slots):
            errors.append('%s: %s' % (msg, slot))
    return errors


# Useful filters for the admin forms

class BaseBlockFilter(admin.SimpleListFilter):
    # Common logic for filtering on Slots and ScheduleItem.slots by block
    # We need to do this as a filter, since we can't use sorting since
    # day is dynamic (either the model field or the previous_slot)
    title = _('Block')
    parameter_name = 'block'

    def lookups(self, request, model_admin):
        # List filter wants the value to be a string, so we use
        # pk to avoid bouncing through strptime.
        return [('%d' % block.pk, str(block)) for
                block in ScheduleBlock.objects.all()]

    def _get_slots(self):
        if self.value():
            block_pk = int(self.value())
            block = ScheduleBlock.objects.get(pk=block_pk)
            # Find all slots with a start_time are in the given block
            slots = list(Slot.objects.filter(
                start_time__gte=block.start_time,
                end_time__lte=block.end_time))
            all_slots = slots[:]
            # Extend with all the slots that have a previous slot
            # Return the filtered list of slot ids
            while Slot.objects.filter(previous_slot__in=slots).exists():
                slots = list(Slot.objects.filter(
                    previous_slot__in=slots).all())
                all_slots.extend(slots)
            return [x.pk for x in all_slots]
        return None


class SlotBlockFilter(BaseBlockFilter):
    # Allow filtering slots by the block, to make editing slots easier

    def queryset(self, request, queryset):
        slot_ids = self._get_slots()
        if slot_ids is not None:
            return queryset.filter(pk__in=slot_ids)
        # No value, so no filtering
        return queryset


class ScheduleItemBlockFilter(BaseBlockFilter):
    # Allow filtering scheduleitems by the day, to make editing easier

    def queryset(self, request, queryset):
        slot_ids = self._get_slots()
        if slot_ids is not None:
            return queryset.filter(slots__pk__in=slot_ids)
        # No value, so no filtering
        return queryset


class BaseStartTimeFilter(admin.SimpleListFilter):
    # Common logic for filtering on Slots and ScheduleItem.slots by start_time
    title = _('Start Time')
    parameter_name = 'start'

    def lookups(self, request, model_admin):
        values = [slot.get_formatted_start_time() for slot in Slot.objects.all()]
        # We order drop duplicates and order globally.
        values = sorted(set(values))
        # It's not great to use the string value as the admin key, but we
        # don't have a better way of dealing with it unfortunately.
        return zip(values, values)

    def _get_slots(self):
        # We choose to filter on the range from %H:%M:00 to %H:%M:59
        # because, while second specifications are possible,
        # we're only using the %H:%M values in lookups, as that matches the
        # schedule display.
        if self.value():
            base_time = datetime.datetime.strptime(self.value(), '%H:%M')
            max_time = base_time + datetime.timedelta(seconds=59)
            # We find all start times between base_time and max_time
            # or slots with the previous_slot end time in this range
            slots = Slot.objects.filter(
                Q(start_time__time__gte=base_time.time(),
                  start_time__time__lte=max_time.time()) |
                Q(previous_slot__end_time__time__gte=base_time.time(),
                  previous_slot__end_time__time__lte=max_time.time()))
            # Return the queryset
            return slots
        return None


class SlotStartTimeFilter(BaseStartTimeFilter):
    # Allow filtering slots by the start_time

    def queryset(self, request, queryset):
        query = self._get_slots()
        if query:
            return query
        # No value, so no filtering
        return queryset


class ScheduleItemStartTimeFilter(BaseStartTimeFilter):
    # Allow filtering scheduleitems by the start time

    def queryset(self, request, queryset):
        query = self._get_slots()
        if query:
            slots = list(query)
            return queryset.filter(slots__in=slots)
        # No value, so no filtering
        return queryset


class ScheduleItemVenueFilter(admin.SimpleListFilter):
    # Allow filtering schedule item by venue
    title = _('Venue')
    parameter_name = 'venue'

    def lookups(self, request, model_admin):
        return [('%d' % venue.pk, str(venue)) for venue in Venue.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            # Filter by venue id
            return queryset.filter(venue__pk=int(self.value()))
        # No value, so no filtering
        return queryset


# Actual admin forms and so forth
class ScheduleItemAdminForm(forms.ModelForm):
    class Meta:
        model = ScheduleItem
        readonly_fields = ('last_updated',)
        fields = ('slots', 'venue', 'talk', 'page', 'details', 'notes',
                  'css_class', 'expand')

    def __init__(self, *args, **kwargs):
        super(ScheduleItemAdminForm, self).__init__(*args, **kwargs)
        self.fields['talk'].queryset = Talk.objects.filter(
            Q(status=ACCEPTED) | Q(status=CANCELLED))
        # Present all pages as possible entries in the schedule
        self.fields['page'].queryset = Page.objects.all()


class ScheduleItemAdmin(CompareVersionAdmin):
    form = ScheduleItemAdminForm

    change_list_template = 'admin/scheduleitem_list.html'
    readonly_fields = ('list_css_classes',)
    list_display = ('get_start_time', 'venue', 'get_title', 'expand')
    list_editable = ('expand',)

    list_filter = (ScheduleItemBlockFilter, ScheduleItemStartTimeFilter,
                   ScheduleItemVenueFilter)
    autocomplete_fields = ('slots',)

    # We stuff these validation results into the view, rather than
    # enforcing conditions on the actual model, since it can be hard
    # to edit the schedule and keep it entirely consistent at every
    # step (think exchanging talks and so forth)
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Find issues in the schedule
        all_items = prefetch_schedule_items()
        errors = defaultdict(list)
        for validator, err_type, _msg in SCHEDULE_ITEM_VALIDATORS:
            failed_items = validator(all_items)
            if failed_items:
                errors[err_type].extend(failed_items)
        extra_context['errors'] = errors
        return super(ScheduleItemAdmin, self).changelist_view(request,
                                                              extra_context)

    def get_urls(self):
        from wafer.schedule.views import ScheduleEditView

        urls = super(ScheduleItemAdmin, self).get_urls()
        admin_schedule_edit_view = self.admin_site.admin_view(
            ScheduleEditView.as_view())
        my_urls = [
            url(r'^edit/$', admin_schedule_edit_view, name='schedule_editor'),
            url(r'^edit/(?P<block_id>[0-9]+)$', admin_schedule_edit_view,
                name='schedule_editor'),
        ]
        return my_urls + urls


class SlotAdminForm(forms.ModelForm):

    class Meta:
        model = Slot
        fields = ('name', 'previous_slot', 'start_time', 'end_time')

    class Media:
        js = ('js/scheduledatetime.js',)


class SlotAdminAddForm(SlotAdminForm):

    # Additional field added for creating multiple slots at once
    additional = forms.IntegerField(min_value=0, max_value=30, required=False,
                                    label=_("Additional slots"),
                                    help_text=_("Create this number of "
                                                "additional slots following "
                                                "this one"))


class SlotAdmin(CompareVersionAdmin):
    form = SlotAdminForm

    list_display = ('__str__', 'get_block', 'get_formatted_start_date_time',
                    'end_time')
    list_editable = ('end_time',)

    change_list_template = 'admin/slot_list.html'

    search_fields = ('name', 'start_time', 'end_time')

    list_filter = (SlotBlockFilter, SlotStartTimeFilter)

    class Media:
        js = ('js/scheduledatetime.js',)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Find issues with the slots
        errors = defaultdict(list)
        all_slots = prefetch_slots()
        for validator, err_type, _msg in SLOT_VALIDATORS:
            failed_slots = validator(all_slots)
            if failed_slots:
                errors[err_type].extend(failed_slots)
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
        if not change and form.cleaned_data['additional']:
            # We add the requested additional slots
            # All created slot will have the same length as the slot just
            # created , and we specify them as a sequence using
            # "previous_slot" so tweaking start times is simple.
            prev = obj
            end = prev.end_time
            start = prev.get_start_time()
            slot_len = end - start
            for loop in range(form.cleaned_data['additional']):
                end = end + slot_len
                new_slot = Slot(previous_slot=prev,
                                end_time=end)
                # Make sure we're valid before adding to the database
                try:
                    new_slot.full_clean()
                    new_slot.save()
                    msgdict = {'obj': force_text(new_slot)}
                    msg = _("Additional slot %(obj)s added sucessfully") % msgdict
                    if hasattr(request, '_messages'):
                        # Don't add messages unless we have a suitable request
                        # Needed during testing, and possibly in other cases
                        self.message_user(request, msg, messages.SUCCESS)
                    prev = new_slot
                except ValidationError as err:
                    msg = _("Failed to create new slot - %s" % err)
                    if hasattr(request, '_messages'):
                        self.message_user(request, msg, messages.ERROR)
                    else:
                        # Useful in testing
                        raise
                    break


# Register and setup reversion support for Blocks and Venues
class ScheduleBlockAdminForm(forms.ModelForm):
    """Admin for blocks with better time display."""
    class Meta:
        model = ScheduleBlock
        fields = ('start_time', 'end_time')

    class Media:
        js = ('js/scheduledatetime.js',)


class ScheduleBlockAdmin(VersionAdmin):
    form = ScheduleBlockAdminForm


class VenueAdmin(VersionAdmin):
    pass


admin.site.register(ScheduleBlock, ScheduleBlockAdmin)
admin.site.register(Slot, SlotAdmin)
admin.site.register(Venue, VenueAdmin)
admin.site.register(ScheduleItem, ScheduleItemAdmin)
