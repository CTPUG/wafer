from django_medusa.renderers import StaticSiteRenderer
from wafer.sponsors.models import Sponsor
from django.core.urlresolvers import reverse


class SponsorRenderer(StaticSiteRenderer):
    def get_paths(self):
        paths = ["/sponsors/", ]

        items = Sponsor.objects.all()
        for item in items:
            paths.append(item.get_absolute_url())
        paths.append(reverse('wafer_sponsors'))
        paths.append(reverse('wafer_sponsorship_packages'))
        return paths


renderers = [SponsorRenderer, ]
