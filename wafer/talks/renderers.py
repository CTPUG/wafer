from django_medusa.renderers import StaticSiteRenderer
from wafer.talks.models import Talk, ACCEPTED


class TalksRenderer(StaticSiteRenderer):
    def get_paths(self):
        paths = ["/talks/", ]

        items = Talk.objects.filter(status=ACCEPTED)
        for item in items:
            paths.append(item.get_absolute_url())
        return paths

renderers = [TalksRenderer, ]
