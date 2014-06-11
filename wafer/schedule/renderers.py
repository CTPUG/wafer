from django_medusa.renderers import StaticSiteRenderer


class ScheduleRenderer(StaticSiteRenderer):
    def get_paths(self):
        paths = ["/schedule/", ]
        return paths

renderers = [ScheduleRenderer, ]
