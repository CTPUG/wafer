from django_medusa.renderers import StaticSiteRenderer
from wafer.pages.models import Page


class PagesRenderer(StaticSiteRenderer):
    def get_paths(self):
        paths = []

        items = Page.objects.all()
        for item in items:
            if item.exclude_from_static:
                # Container page
                continue
            url = item.get_absolute_url()
            paths.append(url)
        return paths

renderers = [PagesRenderer, ]
