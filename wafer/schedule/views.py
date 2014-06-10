from django.views.generic import DetailView, TemplateView

from wafer.schedule.models import Venue, Day, Slot
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


class ScheduleView(TemplateView):
    template_name = 'wafer.schedule/full_schedule.html'

    def get_context_data(self, **kwargs):
        context = super(ScheduleView, self).get_context_data(**kwargs)
        # Check if the schedule is valid
        if not check_schedule():
            return context
        venue_list = list(Venue.objects.all())
        context['venue_list'] = venue_list
        # We create a list of slots and schedule items
        schedule_days = {}
        seen_items = {}
        for day in Day.objects.all():
            schedule_days.setdefault(day, [])
            # Because of Slot.previous_slot juggling, we can't just use
            # the related objects to get all the slots
            slots = [x for x in Slot.objects.all() if x.get_day() == day]
            for slot in slots:
                row = ScheduleRow(slot, venue_list)
                schedule_days[day].append(row)
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
        # We turn the dict into a list here so we have the correct
        # ordering
        context['table_days'] = sorted(schedule_days.items())

        return context
