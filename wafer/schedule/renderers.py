from django_medusa.renderers import StaticSiteRenderer
from wafer.schedule.models import Venue


class ScheduleRenderer(StaticSiteRenderer):
    def get_paths(self):
        paths = ["/schedule/", "/schedule/pentabarf.xml"]

        # Add the venues
        items = Venue.objects.all()
        for item in items:
            paths.append(item.get_absolute_url())
        return paths

renderers = [ScheduleRenderer, ]
