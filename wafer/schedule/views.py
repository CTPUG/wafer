from django.views.generic import DetailView, TemplateView
from django.conf import settings

from wafer.schedule.models import Venue, ScheduleItem


class ScheduleRow(object):
    """This is a helpfule containter for the schedule view to keep sanity"""
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


class VenueView(DetailView):
    template_name = 'wafer.schedule/venue.html'
    model = Venue


class ScheduleView(TemplateView):
    template_name = 'wafer.schedule/full_schedule.html'

    def get_context_data(self, **kwargs):
        context = super(ScheduleView, self).get_context_data(**kwargs)
        venue_list = list(Venue.objects.all())
        context['venue_list'] = venue_list
        # We create a list of slots and schedule items
        days = {}
        # This can be made efficient, be we run multiple passes so the
        # logic involves less back-tracking
        used_venues = {}
        for item in ScheduleItem.objects.all():
            slots = list(item.slots.all())
            # We should be dealing with single timezone, so this is safe
            day = slots[0].start_time.date()
            if day not in days:
                days.setdefault(day, [])
            rowspan = 0
            append_row = None
            for slot in slots:
                used_venues.setdefault(slot, {})
                found = False
                for row in days[day]:
                    if row.slot == slot:
                        found = True
                        if rowspan == 0:
                            append_row = row
                        rowspan += 1
                if not days[day] or not found:
                    row = ScheduleRow(slot, venue_list)
                    days[day].append(row)
                    if rowspan == 0:
                        append_row = row
                    rowspan += 1
            scheditem = {'item': item, 'rowspan': rowspan, 'colspan': 1}
            append_row.items[item.venue] = scheditem
            for slot in slots:
                used_venues[slot][item.venue] = scheditem
        # Need to fix up col spans
        for day, rows in days.iteritems():
            for table_row in rows:
                if len(table_row.items) == len(venue_list):
                    # All venues filled
                    continue
                cur_item = None
                colspan = 1
                for venue in venue_list:
                    if venue not in used_venues[table_row.slot]:
                        colspan += 1
                    else:
                        if cur_item:
                            cur_item['colspan'] = colspan
                            colspan = 1
                        cur_item = used_venues[table_row.slot][venue]
                        cur_item['colspan'] = colspan
                cur_item['colspan'] = colspan

        context['table_days'] = days

        return context
