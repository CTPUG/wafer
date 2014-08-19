import datetime
from django.views.generic import DetailView, TemplateView

from wafer.schedule.models import Venue, Slot, Day
from wafer.schedule.admin import check_schedule


class ScheduleRow(object):
    """This is a helpful containter for the schedule view to keep sanity"""
    def __init__(self, slot, venue_list):
        self.slot = slot
        self.venue_list = venue_list
        self.items = {}

    def get_sorted_items(self):
        sorted_items = []
        for venue in self.venue_list:
            if venue in self.items:
                sorted_items.append(self.items[venue])
        return sorted_items

    def __repr__(self):
        """Debugging aid"""
        return '%s - %s' % (self.slot, self.get_sorted_items())


class VenueView(DetailView):
    template_name = 'wafer.schedule/venue.html'
    model = Venue



def make_schedule_row(venue_list, slot, seen_items):
    """Create a row for the schedule table."""
    day = slot.get_day()
    row = ScheduleRow(slot, venue_list)
    skip = []
    for item in slot.scheduleitem_set.all():
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
    for venue in venue_list:
        # This may create holes in the table - the administrator
        # needs to sort that out by ordering the venues correctly
        if day not in venue.days.all():
            scheditem = {'item': 'unavailable',
                         'rowspan': 1, 'colspan': 1}
            row.items[venue] = scheditem
            # Make holes more obvious
            cur_item = scheditem
            colspan = 1
        elif venue in skip:
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


def generate_schedule_dict(venue_list, today=None):
    """Helper function which creates a dictionary of the schedule"""
    # We create a list of slots and schedule items
    schedule_days = {}
    seen_items = {}
    for slot in Slot.objects.all().order_by('end_time', 'start_time', 'day'):
        day = slot.get_day()
        if today and day != today:
            # Restrict ourselves to only today
            continue
        schedule_days.setdefault(day, [])
        row = make_schedule_row(venue_list, slot, seen_items)
        schedule_days[day].append(row)
    return schedule_days


class ScheduleView(TemplateView):
    template_name = 'wafer.schedule/full_schedule.html'

    def get_context_data(self, **kwargs):
        context = super(ScheduleView, self).get_context_data(**kwargs)
        # Check if the schedule is valid
        if not check_schedule():
            return context
        venue_list = list(Venue.objects.all())
        context['venue_list'] = venue_list
        schedule_days = generate_schedule_dict(venue_list)
        # We turn the dict into a list here so we have a specified
        # ordering by date
        context['table_days'] = sorted(schedule_days.items(),
                                       key=lambda x: x[0].date)

        return context


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
        day = self.request.GET.get('day', datetime.date.today())
        dates = dict([(x.date.strftime('%Y-%m-%d'), x) for x in
                      Day.objects.all()])
        if day not in dates:
            # Nothing happening today
            return context
        # get the associated day object
        today = dates[day]
        now = datetime.datetime.now().time()
        if 'time' in  self.request.GET:
            time = self.request.GET['time']
            try:
                time = datetime.datetime.strptime(time, '%H:%M').time()
            except ValueError:
                time = now
        else:
            time = now
        venue_list = list(Venue.objects.all())
        context['venue_list'] = venue_list
        # Find the slot that includes now
        cur_slot = None
        prev_slot = None
        next_slot = None
        for slot in Slot.objects.all():
            if slot.get_day() != today:
                continue
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
        current_items = {}
        seen_items = {}
        context['cur_slot'] = None
        if prev_slot:
            prev_row = make_schedule_row(venue_list, prev_slot, seen_items)
            context['slots'].append(prev_row)
        if cur_slot:
            cur_row = make_schedule_row(venue_list, cur_slot, seen_items)
            for item in cur_row.items.values():
                item['note'] = 'current'
            context['slots'].append(cur_row)
            context['cur_slot'] = cur_slot
        if next_slot:
            next_row = make_schedule_row(venue_list, next_slot, seen_items)
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
