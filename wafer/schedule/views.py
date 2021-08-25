import datetime
import os

import logging

from icalendar import Calendar, Event

from django.conf import settings
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.decorators import method_decorator
from django.views.decorators.http import condition
from django.views.generic import TemplateView, View

from bakery.views import BuildableDetailView, BuildableTemplateView, BuildableMixin
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from wafer import __version__
from wafer.pages.models import Page
from wafer.schedule.models import (
    Venue, Slot, ScheduleBlock, ScheduleItem, get_schedule_version)
from wafer.schedule.admin import check_schedule, validate_schedule
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


def schedule_version_last_modified(request, **kwargs):
    """Return the current schedule version as a datetime"""
    version = get_schedule_version()
    return parse_datetime(version)


@method_decorator(
    condition(last_modified_func=schedule_version_last_modified),
    name='dispatch')
class ScheduleView(BuildableTemplateView):
    template_name = 'wafer.schedule/full_schedule.html'
    build_path = 'schedule/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        context['schedule_version'] = get_schedule_version()
        return context


class ScheduleXmlView(ScheduleView):
    template_name = 'wafer.schedule/penta_schedule.xml'
    content_type = 'application/xml'
    build_path = 'schedule/pentabarf.xml'

    def get_context_data(self, **kwargs):
        """Allow adding a 'render_description' parameter"""
        context = super().get_context_data(**kwargs)
        context['wafer_version'] = __version__
        context['TIME_ZONE'] = settings.TIME_ZONE
        context['WAFER_CONFERENCE_ACRONYM'] = settings.WAFER_CONFERENCE_ACRONYM
        if self.request.GET.get('render_description', None) == '1':
            context['render_description'] = True
        else:
            context['render_description'] = False
        return context


class CurrentView(TemplateView):
    template_name = 'wafer.schedule/current.html'

    def _parse_timestamp(self, timestamp):
        """
        Parse a user provided timestamp query string parameter.
        Return a TZ aware datetime, or None.
        """
        if not timestamp:
            return None
        try:
            timestamp = parse_datetime(timestamp)
        except ValueError as e:
            messages.error(self.request,
                           'Failed to parse timestamp: %s' % e)
        if timestamp is None:
            messages.error(self.request, 'Failed to parse timestamp')
            return None
        if not timezone.is_aware(timestamp):
            timestamp = timezone.make_aware(timestamp)
        return timestamp

    def _get_schedule_page(self, timestamp):
        for candidate in ScheduleBlock.objects.all():
            if candidate.start_time < timestamp < candidate.end_time:
                return SchedulePage(candidate)
        return None

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
        context = super().get_context_data(**kwargs)
        # If the schedule is invalid, return a context with active=False
        context['active'] = False
        if not check_schedule():
            return context
        # The schedule is valid, so add active=True and empty slots
        context['active'] = True
        context['slots'] = []
        # Allow refresh time to be overridden
        context['refresh'] = self.request.GET.get('refresh', None)

        # Allow the current time to be overridden, mostly for testing
        timestamp = self._parse_timestamp(
                self.request.GET.get('timestamp', None)) or timezone.now()

        schedule_page = self._get_schedule_page(timestamp)
        # If there are no items scheduled for today, return an empty slots list
        if schedule_page is None:
            return context
        context['schedule_page'] = schedule_page

        highlight_venue = lookup_highlighted_venue(self.request)
        context['highlight_venue_pk'] = -1
        if highlight_venue is not None:
            context['highlight_venue_pk'] = highlight_venue

        cur_slot, current_rows = self._current_slots(schedule_page, timestamp)
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
        context = super().get_context_data(**kwargs)

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


@method_decorator(
    condition(last_modified_func=schedule_version_last_modified),
    name='dispatch')
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
            sched_event.add('url', item.get_url())
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


@method_decorator(
    condition(last_modified_func=schedule_version_last_modified),
    name='dispatch')
class JsonDataView(View, BuildableMixin):
    build_path = "schedule/schedule.json"

    # Version of the json export, so tools can hopefully track changes
    # sanely
    FORMAT_VERSION = "0.1"

    def get(self, request):
        """Create a json data blob from the schedule"""
        # This is mainly to be consumed by video processes, so we
        # mainly keep the naming conventions from pentabarf for historical compatibility
        #
        # We restrict this to only people with permission to view profile details, since
        # there are already other public views of the schedule for unauthenticated consumers
        if not request.user.is_staff:
            raise PermissionDenied
        site = get_current_site(request)

        data = {
           'conference name': site.name,
           'domain': site.domain,
           'version': self.FORMAT_VERSION,
        }

        data['venues'] = []

        data['events'] = []

        for venue in Venue.objects.all():
            venue_data = {}
            venue_data['id'] = venue.pk
            venue_data['name'] = venue.name
            venue_data['has_video'] = venue.video
            venue_data['details'] = venue.notes
            data['venues'].append(venue_data)

        for item in ScheduleItem.objects.all():
            sched_event = {}
            sched_event['id'] = item.pk
            sched_event['start_time'] = item.get_start_datetime().isoformat()
            sched_event['duration'] = item.get_duration_minutes()
            sched_event['room_id'] = item.venue.pk
            sched_event['title'] = item.get_title()
            sched_event['url'] = item.get_url()
            authors = []
            if item.talk is not None:
                if item.talk.track:
                    sched_event['track'] = item.talk.track
                else:
                    sched_event['track'] = 'No Track'
                # We're not rendering anything, so this is presumably 'safe'
                sched_event['description'] = item.talk.abstract.raw
                sched_event['video_allowed'] = item.talk.video
                for person in item.talk.authors.all():
                    authors.append(person)
            else:
                # Presumably a page, which may not have an author or description
                sched_event['track'] = 'No Track'
                # More complex logic is probably needed here
                sched_event['video_allowed'] = True
                sched_event['description'] = item.page.content.raw
                for person in item.page.people.all():
                    authors.append(person)
            sched_event['authors'] = []
            for person in authors:
                person_data = {
                    'name': person.userprofile.display_name(),
                    'email': person.email
                }
                if person.userprofile.twitter_handle:
                    person_data['twitter'] = person.userprofile.twitter_handle
                sched_event['authors'].append(person_data)
            sched_event['license'] = settings.WAFER_VIDEO_LICENSE
            sched_event['license_url'] = settings.WAFER_VIDEO_LICENSE_URL
            data['events'].append(sched_event)

        response = JsonResponse(data, json_dumps_params={'sort_keys': True})
        return response
