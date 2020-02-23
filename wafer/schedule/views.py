import datetime
import os

import logging

from icalendar import Calendar, Event

from django.db.models import Q
from django.views.generic import TemplateView, View
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings

from bakery.views import BuildableDetailView, BuildableTemplateView, BuildableMixin
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from wafer.pages.models import Page
from wafer.schedule.models import Venue, Slot, ScheduleBlock
from wafer.schedule.admin import check_schedule, validate_schedule
from wafer.schedule.models import ScheduleItem
from wafer.schedule.serializers import ScheduleItemSerializer
from wafer.talks.models import ACCEPTED, CANCELLED
from wafer.talks.models import Talk


logger = logging.getLogger(__name__)


class ScheduleRow(object):
    """This is a helpful containter for the schedule view to keep sanity"""
    def __init__(self, schedule_page, slot):
        self.schedule_page = schedule_page
        self.slot = slot
        self.start_time = slot.get_start_time()
        self.items = {}

    def get_sorted_items(self):
        sorted_items = []
        for venue in self.schedule_page.venues:
            if venue in self.items:
                sorted_items.append(self.items[venue])
        return sorted_items

    def __repr__(self):
        """Debugging aid"""
        return '%s - %s' % (self.slot, self.get_sorted_items())


class SchedulePage(object):
    """A helpful container for information about blocks in a schedule view."""
    def __init__(self, block):
        self.block = block
        self.venues = list(block.venue_set.all())
        self.rows = []


class VenueView(BuildableDetailView):
    template_name = 'wafer.schedule/venue.html'
    model = Venue


def make_schedule_row(schedule_page, slot, seen_items):
    """Create a row for the schedule table."""
    row = ScheduleRow(schedule_page, slot)
    skip = {}
    expanding = {}
    all_items = list(slot.scheduleitem_set
                     .select_related('talk', 'page', 'venue')
                     .all())

    for item in all_items:
        if item in seen_items:
            # Inc rowspan
            seen_items[item]['rowspan'] += 1
            # Note that we need to skip this during colspan checks
            skip[item.venue] = seen_items[item]
            continue
        scheditem = {'item': item, 'rowspan': 1, 'colspan': 1}
        row.items[item.venue] = scheditem
        seen_items[item] = scheditem
        if item.expand:
            expanding[item.venue] = []

    empty = []
    expanding_right = None
    skipping = 0
    skip_item = None
    for venue in schedule_page.venues:
        if venue in skip:
            # We need to skip all the venues this item spans over
            skipping = 1
            skip_item = skip[venue]
            continue
        if venue in expanding:
            item = row.items[venue]
            for empty_venue in empty:
                row.items.pop(empty_venue)
                item['colspan'] += 1
            empty = []
            expanding_right = item
        elif venue in row.items:
            empty = []
            expanding_right = None
        elif expanding_right:
            expanding_right['colspan'] += 1
        elif skipping > 0 and skipping < skip_item['colspan']:
            skipping += 1
        else:
            skipping = 0
            empty.append(venue)
            row.items[venue] = {'item': None, 'rowspan': 1, 'colspan': 1}

    return row


def generate_schedule(this_block=None):
    """Helper function which creates an ordered list of schedule days"""
    # We create a list of slots and schedule items
    schedule_pages = {}
    seen_items = {}
    for slot in Slot.objects.all().order_by('end_time', 'start_time'):
        block = slot.get_block()
        if this_block and block != this_block:
            # Restrict ourselves to only given block
            continue
        schedule_page = schedule_pages.get(block)
        if schedule_page is None:
            schedule_page = schedule_pages[block] = SchedulePage(block)
        row = make_schedule_row(schedule_page, slot, seen_items)
        schedule_page.rows.append(row)
    return sorted(schedule_pages.values(), key=lambda x: x.block.start_time)


def lookup_highlighted_venue(request):
    venue_id = request.GET.get('highlight-venue', None)
    if venue_id:
        try:
            if Venue.objects.get(pk=int(venue_id)):
                return int(venue_id)
        except (ValueError, Venue.DoesNotExist):
            logger.warn('Invalid venue id passed to schedule: %s' % venue_id)
    return None


class ScheduleView(BuildableTemplateView):
    template_name = 'wafer.schedule/full_schedule.html'
    build_path = 'schedule/index.html'

    def get_context_data(self, **kwargs):
        context = super(ScheduleView, self).get_context_data(**kwargs)
        # Check if the schedule is valid
        context['active'] = False
        context['prev_block'] = None
        context['next_block'] = None
        if not check_schedule():
            return context
        context['active'] = True
        try:
            block_id = int(self.request.GET.get('block', -1))
        except ValueError:
            block_id = -1
        blocks = ScheduleBlock.objects.all()
        try:
            this_block = blocks.get(id=block_id)
        except ObjectDoesNotExist:
            # We choose to return the full schedule if given an invalid block id
            this_block = None
        highlight_venue = lookup_highlighted_venue(self.request)
        context['highlight_venue_pk'] = -1
        if highlight_venue is not None:
            context['highlight_venue_pk'] = highlight_venue
        if this_block:
            # Add next / prev blocks links
            # blocks are sorted by time by default
            blocks = list(blocks)
            pos = blocks.index(this_block)
            if pos > 0:
                context['prev_block'] = blocks[pos - 1]
            if pos < len(blocks) - 1:
                context['next_block'] = blocks[pos + 1]
        context['schedule_pages'] = generate_schedule(this_block)
        return context


class ScheduleXmlView(ScheduleView):
    template_name = 'wafer.schedule/penta_schedule.xml'
    content_type = 'application/xml'
    build_path = 'schedule/pentabarf.xml'

    def get_context_data(self, **kwargs):
        """Allow adding a 'render_description' parameter"""
        context = super(ScheduleXmlView, self).get_context_data(**kwargs)
        if self.request.GET.get('render_description', None) == '1':
            context['render_description'] = True
        else:
            context['render_description'] = False
        return context


class CurrentView(TemplateView):
    template_name = 'wafer.schedule/current.html'

    def _parse_today(self, day):
        if day is None:
            day = datetime.date.today()
        else:
            day = datetime.datetime.strptime(day, '%Y-%m-%d').date()
        for candidate in ScheduleBlock.objects.all():
            if candidate.start_time.date() <= day and candidate.end_time.date() >= day:
                return SchedulePage(candidate)
        return None

    def _parse_time(self, day, time):
        tz = timezone.get_default_timezone()
        now = timezone.make_aware(datetime.datetime.now(), tz)
        if day is None:
            return now
        if time is None:
            return now
        try:
            full_time = datetime.datetime.combine(datetime.datetime.strptime(day, "%Y-%m-%d").date(),
                                                  datetime.datetime.strptime(time, '%H:%M').time())
            return timezone.make_aware(full_time, tz)
        except ValueError:
            pass
        return now

    def _add_note(self, row, note, overlap_note):
        for item in row.items.values():
            if item['rowspan'] == 1:
                item['note'] = note
            else:
                # Must overlap with current slot
                item['note'] = overlap_note

    def _current_slots(self, schedule_page, search_time):
        cur_slot, prev_slot, next_slot = None, None, None
        for slot in Slot.objects.all():
            if (slot.get_start_time() > schedule_page.block.end_time or
                    slot.end_time < schedule_page.block.start_time):
                continue
            if slot.get_start_time() <= search_time < slot.end_time:
                cur_slot = slot
            elif slot.end_time <= search_time:
                if not prev_slot or prev_slot.end_time < slot.end_time:
                    prev_slot = slot
            elif slot.get_start_time() >= search_time:
                if not next_slot or next_slot.end_time > slot.end_time:
                    next_slot = slot
        cur_rows = self._current_rows(
            schedule_page, cur_slot, prev_slot, next_slot)
        return cur_slot, cur_rows

    def _current_rows(self, schedule_page, cur_slot, prev_slot, next_slot):
        seen_items = {}
        rows = []
        for slot in (prev_slot, cur_slot, next_slot):
            if slot:
                row = make_schedule_row(schedule_page, slot, seen_items)
            else:
                row = None
            rows.append(row)
        # Add styling hints. Needs to be after all the schedule rows are
        # created so the spans are set correctly
        if prev_slot:
            self._add_note(rows[0], 'complete', 'current')
        if cur_slot:
            self._add_note(rows[1], 'current', 'current')
        if next_slot:
            self._add_note(rows[2], 'forthcoming', 'current')
        return [r for r in rows if r]

    def get_context_data(self, **kwargs):
        context = super(CurrentView, self).get_context_data(**kwargs)
        # If the schedule is invalid, return a context with active=False
        context['active'] = False
        if not check_schedule():
            return context
        # The schedule is valid, so add active=True and empty slots
        context['active'] = True
        context['slots'] = []
        # Allow refresh time to be overridden
        context['refresh'] = self.request.GET.get('refresh', None)
        # If there are no items scheduled for today, return an empty slots list
        schedule_page = self._parse_today(self.request.GET.get('day', None))
        if schedule_page is None:
            return context
        context['schedule_page'] = schedule_page
        # Allow current time to be overridden
        time = self._parse_time(self.request.GET.get('day', None), self.request.GET.get('time', None))

        highlight_venue = lookup_highlighted_venue(self.request)
        context['highlight_venue_pk'] = -1
        if highlight_venue is not None:
            context['highlight_venue_pk'] = highlight_venue

        cur_slot, current_rows = self._current_slots(schedule_page, time)
        context['cur_slot'] = cur_slot
        context['slots'].extend(current_rows)

        return context


class ScheduleItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = ScheduleItem.objects.all().order_by('id')
    serializer_class = ScheduleItemSerializer
    permission_classes = (IsAdminUser, )


class ScheduleEditView(TemplateView):
    template_name = 'wafer.schedule/edit_schedule.html'

    def _slot_context(self, slot, venues):
        slot_context = {
            'name': slot.name,
            'start_time': slot.get_start_time(),
            'end_time': slot.end_time,
            'id': slot.id,
            'venues': []
        }
        for venue in venues:
            venue_context = {
                'name': venue.name,
                'id': venue.id,
            }
            for schedule_item in slot.scheduleitem_set.all():
                if schedule_item.venue.name == venue.name:
                    venue_context['scheduleitem_id'] = schedule_item.id
                    if schedule_item.talk:
                        talk = schedule_item.talk
                        venue_context['title'] = talk.title
                        venue_context['talk'] = talk
                    if (schedule_item.page and
                            not schedule_item.page.exclude_from_static):
                        page = schedule_item.page
                        venue_context['title'] = page.name
                        venue_context['page'] = page
            slot_context['venues'].append(venue_context)
        return slot_context

    def get_context_data(self, block_id=None, **kwargs):
        context = super(ScheduleEditView, self).get_context_data(**kwargs)

        blocks = ScheduleBlock.objects.all()
        if block_id:
            block = blocks.get(id=block_id)
        else:
            block = blocks.first()

        public_talks = Talk.objects.filter(Q(status=ACCEPTED) |
                                           Q(status=CANCELLED))
        public_talks = public_talks.order_by("talk_type", "talk_id")
        venues = Venue.objects.filter(blocks__in=[block])
        slots = Slot.objects.all().select_related(
            'previous_slot').prefetch_related(
            'scheduleitem_set', 'slot_set').order_by(
                'end_time', 'start_time')
        aggregated_slots = []

        for slot in slots:
            if block != slot.get_block():
                continue
            aggregated_slots.append(self._slot_context(slot, venues))

        context['this_block'] = block
        context['venues'] = venues
        context['slots'] = aggregated_slots
        context['talks_all'] = public_talks
        context['talks_unassigned'] = public_talks.filter(scheduleitem=None)
        context['pages'] = Page.objects.all()
        context['all_blocks'] = blocks
        context['validation_errors'] = validate_schedule()
        return context


class ICalView(View, BuildableMixin):
    build_path = 'schedule/schedule.ics'

    def get(self, request):
        """Create a iCal file from the schedule"""
        # Heavily inspired by https://djangosnippets.org/snippets/2223/ and
        # the icalendar documentation
        calendar = Calendar()
        site = get_current_site(request)
        calendar.add('prodid', '-//%s Schedule//%s//' % (site.name, site.domain))
        calendar.add('version', '2.0')

        # Since we don't need to format anything here, we can just use a list
        # of schedule items
        for item in ScheduleItem.objects.all():
            sched_event = Event()
            sched_event.add('dtstamp', item.last_updated)
            sched_event.add('summary', item.get_title())
            sched_event.add('location', item.venue.name)
            sched_event.add('dtstart', item.get_start_datetime())
            sched_event.add('duration', datetime.timedelta(minutes=item.get_duration_minutes()))
            sched_event.add('class', 'PUBLIC')
            sched_event.add('uid', '%s@%s' % (item.pk, site.domain))
            calendar.add_component(sched_event)
        response = HttpResponse(calendar.to_ical(), content_type="text/calendar")
        response['Content-Disposition'] = 'attachment; filename=schedule.ics'
        return response

    def get_content(self):
        """Return just the iCal data for bakery"""
        response = self.get(self.request)
        return response.content

    @property
    def build_method(self):
        return self.build

    def build(self):
        logger.debug("Building iCal schedule in %s" % (
            self.build_path,
        ))
        self.request = self.create_request(self.build_path)
        path = os.path.join(settings.BUILD_DIR, self.build_path)
        self.prep_directory(self.build_path)
        self.build_file(path, self.get_content())
