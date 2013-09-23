from django.views.generic import DetailView, TemplateView
from django.conf import settings

from wafer.schedule.models import Venue, ScheduleItem


class ScheduleRow(object):
    """This is a helpfule containter for the schedule view to keep sanity"""
    def __init__(self, slot):
        self.slot = slot
        self.items = []


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
        for item in ScheduleItem.objects.all():
            slots = list(item.slots.all())
            day = slots[0].start_time.date()
            if day not in days:
                days.setdefault(day, [])
            rowspan = 0
            append_row = None
            for slot in slots:
                found = False
                for row in days[day]:
                    if row.slot == slot:
                        found = True
                        if rowspan == 0:
                            append_row = row
                        else:
                            # Flag this as blank
                            row.append(None)
                        rowspan += 1
                if not days[day] or not found:
                    row = ScheduleRow(slot)
                    days[day].append(row)
                    if rowspan == 0:
                        append_row = row
                    else:
                        # Flag this as blank
                        row.append(None)
                    rowspan += 1
            scheditem = {'item': item, 'rowspan': rowspan, 'colspan': 1}
            append_row.items.append(scheditem)
        # Need to fix up col spans
        for day, rows in days.iteritems():
            for table_row in rows:
                if len(table_row.items) == len(venue_list):
                    # All venues filled
                    continue

        context['table_days'] = days

        return context
