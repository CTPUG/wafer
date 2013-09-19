from django.views.generic import DetailView
from django.conf import settings

from wafer.schedule.models import Venue, ScheduleItem

class VenueView(DetailView):
    template_name = 'wafer.schedule/venue.html'
    model = Venue


class ScheduleView(DetailView):
    template_name = 'wafer.schedule/full_schedule.html'
