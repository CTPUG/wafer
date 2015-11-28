import datetime

from django.views.generic import DetailView, TemplateView

from rest_framework import viewsets
from wafer.pages.models import Page
from wafer.schedule.models import Venue, Slot, Day
from wafer.schedule.admin import check_schedule
from wafer.schedule.models import ScheduleItem
from wafer.schedule.serializers import ScheduleItemSerializer
from wafer.talks.models import ACCEPTED
from wafer.talks.models import Talk


class ScheduleRow(object):
    """This is a helpful containter for the schedule view to keep sanity"""
    def __init__(self, schedule_day, slot):
        self.schedule_day = schedule_day
        self.slot = slot
        self.items = {}

    def get_sorted_items(self):
        sorted_items = []
        for venue in self.schedule_day.venues:
            if venue in self.items:
                sorted_items.append(self.items[venue])
        return sorted_items

    def __repr__(self):
        """Debugging aid"""
        return '%s - %s' % (self.slot, self.get_sorted_items())


class ScheduleDay(object):
    """A helpful container for information a days in a schedule view."""
    def __init__(self, day):
        self.day = day
        self.venues = list(day.venue_set.all())
        self.rows = []


class VenueView(DetailView):
    template_name = 'wafer.schedule/venue.html'
    model = Venue


def make_schedule_row(schedule_day, slot, seen_items):
    """Create a row for the schedule table."""
    row = ScheduleRow(schedule_day, slot)
    skip = []
    all_items = list(slot.scheduleitem_set
                     .select_related('talk', 'page', 'venue')
                     .all())

    for item in all_items:
        if item in seen_items:
            # Inc rowspan
            seen_items[item]['rowspan'] += 1
            # Note that we need to skip this during colspan checks
            skip.append(item.venue)
            continue
        scheditem = {'item': item, 'rowspan': 1, 'colspan': 1}
        row.items[item.venue] = scheditem
        seen_items[item] = scheditem
    cur_item = None
    colspan = 1
    # Fixup colspans
    for venue in schedule_day.venues:
        if venue in skip:
            # Nothing to see here
            continue
        elif venue not in row.items:
            if cur_item:
                cur_item['colspan'] += 1
            else:
                colspan += 1
        else:
            cur_item = row.items[venue]
            cur_item['colspan'] = colspan
            colspan = 1
    return row


def generate_schedule(today=None):
    """Helper function which creates an ordered list of schedule days"""
    # We create a list of slots and schedule items
    schedule_days = {}
    seen_items = {}
    for slot in Slot.objects.all().order_by('end_time', 'start_time', 'day'):
        day = slot.get_day()
        if today and day != today:
            # Restrict ourselves to only today
            continue
        schedule_day = schedule_days.get(day)
        if schedule_day is None:
            schedule_day = schedule_days[day] = ScheduleDay(day)
        row = make_schedule_row(schedule_day, slot, seen_items)
        schedule_day.rows.append(row)
    return sorted(schedule_days.values(), key=lambda x: x.day.date)


class ScheduleView(TemplateView):
    template_name = 'wafer.schedule/full_schedule.html'

    def get_context_data(self, **kwargs):
        context = super(ScheduleView, self).get_context_data(**kwargs)
        # Check if the schedule is valid
        context['active'] = False
        context['days'] = Day.objects.all()
        if not check_schedule():
            return context
        context['active'] = True
        day = self.request.GET.get('day', None)
        dates = dict([(x.date.strftime('%Y-%m-%d'), x) for x in
                      Day.objects.all()])
        # We choose to return the full schedule if given an invalid date
        day = dates.get(day, None)
        context['schedule_days'] = generate_schedule(day)
        return context


class ScheduleXmlView(ScheduleView):
    template_name = 'wafer.schedule/penta_schedule.xml'
    content_type = 'application/xml'


class CurrentView(TemplateView):
    template_name = 'wafer.schedule/current.html'

    def get_context_data(self, **kwargs):
        context = super(CurrentView, self).get_context_data(**kwargs)
        # Check if the schedule is valid
        context['active'] = False
        if not check_schedule():
            return context
        # schedule is valid, so
        context['active'] = True
        context['slots'] = []
        # We allow url parameters to override the default
        context['refresh'] = self.request.GET.get('refresh', None)
        day = self.request.GET.get('day', str(datetime.date.today()))
        dates = dict([(x.date.strftime('%Y-%m-%d'), x) for x in
                      Day.objects.all()])
        if day not in dates:
            # Nothing happening today
            return context
        # get the associated day object
        today = dates[day]
        now = datetime.datetime.now().time()
        if 'time' in self.request.GET:
            time = self.request.GET['time']
            try:
                time = datetime.datetime.strptime(time, '%H:%M').time()
            except ValueError:
                time = now
        else:
            time = now
        # Find the slot that includes now
        cur_slot = None
        prev_slot = None
        next_slot = None
        schedule_day = None
        for slot in Slot.objects.all():
            if slot.get_day() != today:
                continue
            if schedule_day is None:
                schedule_day = ScheduleDay(slot.get_day())
            if slot.get_start_time() <= time and slot.end_time > time:
                cur_slot = slot
            elif slot.end_time <= time:
                if prev_slot:
                    if prev_slot.end_time < slot.end_time:
                        prev_slot = slot
                else:
                    prev_slot = slot
            elif slot.get_start_time() >= time:
                if next_slot:
                    if next_slot.end_time > slot.end_time:
                        next_slot = slot
                else:
                    next_slot = slot
        seen_items = {}
        context['cur_slot'] = None
        context['schedule_day'] = schedule_day
        if prev_slot:
            prev_row = make_schedule_row(schedule_day, prev_slot, seen_items)
            context['slots'].append(prev_row)
        if cur_slot:
            cur_row = make_schedule_row(schedule_day, cur_slot, seen_items)
            for item in cur_row.items.values():
                item['note'] = 'current'
            context['slots'].append(cur_row)
            context['cur_slot'] = cur_slot
        if next_slot:
            next_row = make_schedule_row(schedule_day, next_slot, seen_items)
            context['slots'].append(next_row)
        # Add styling hints. Needs to be after all the schedule rows are
        # created so the spans are set correctly
        if prev_slot:
            for item in prev_row.items.values():
                if item['rowspan'] == 1:
                    item['note'] = 'complete'
                else:
                    # Must overlap with current slot
                    item['note'] = 'current'
        if next_slot:
            for item in next_row.items.values():
                if item['rowspan'] == 1:
                    item['note'] = 'forthcoming'
                else:
                    # Must overlap with current slot
                    item['note'] = 'current'
        return context


class ScheduleItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = ScheduleItem.objects.all()
    serializer_class = ScheduleItemSerializer


class ScheduleEditView(TemplateView):
    template_name = 'wafer.schedule/edit_schedule.html'

    def get_context_data(self, day_id=None, **kwargs):
        context = super(ScheduleEditView, self).get_context_data(**kwargs)

        days = Day.objects.all()

        day = days.first()
        if day_id:
            day = days.get(id=day_id)

        accepted_talks = Talk.objects.filter(status=ACCEPTED)
        venues = Venue.objects.filter(days__in=[day])
        slots = Slot.objects.all().select_related(
            'day', 'previous_slot').prefetch_related(
            'scheduleitem_set', 'slot_set').order_by(
                'end_time', 'start_time', 'day')
        aggregated_slots = []

        for slot in slots:
            slot_day = slot.get_day()
            if day != slot_day:
                continue
            aggregated_slot = {
                'name': slot.name,
                'start_time': slot.get_start_time(),
                'end_time': slot.end_time,
                'id': slot.id,
                'venues': []
            }
            for venue in venues:
                aggregated_venue = {
                    'name': venue.name,
                    'id': venue.id,
                }
                for schedule_item in slot.scheduleitem_set.all():
                    if schedule_item.venue.name == venue.name:
                        if schedule_item.talk:
                            talk = schedule_item.talk
                            aggregated_venue['title'] = talk.title
                            aggregated_venue['talk'] = talk
                            aggregated_venue['scheduleitem_id'] = talk.talk_id
                        if (schedule_item.page and
                                not schedule_item.page.exclude_from_static):
                            page = schedule_item.page
                            aggregated_venue['title'] = page.name
                            aggregated_venue['page'] = page
                            aggregated_venue['scheduleitem_id'] = page.id

                aggregated_slot['venues'].append(aggregated_venue)
            aggregated_slots.append(aggregated_slot)

        context['day'] = day
        context['venues'] = venues
        context['slots'] = aggregated_slots
        context['talks_all'] = accepted_talks
        context['talks_unassigned'] = accepted_talks.filter(scheduleitem=None)
        context['pages'] = Page.objects.all()
        context['days'] = days
        return context
