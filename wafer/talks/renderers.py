from django_medusa.renderers import StaticSiteRenderer
from wafer.talks.models import Talk, ACCEPTED
from wafer.talks.views import UsersTalks
from django.core.urlresolvers import reverse


class TalksRenderer(StaticSiteRenderer):
    def get_paths(self):
        paths = ["/talks/", ]

        items = Talk.objects.filter(status=ACCEPTED)
        for item in items:
            paths.append(item.get_absolute_url())
        view = UsersTalks()
        view.request = None
        queryset = view.get_queryset()
        paginator = view.get_paginator(queryset,
                                       view.get_paginate_by(queryset))
        for page in paginator.page_range:
            paths.append(reverse('wafer_users_talks_page',
                                 kwargs={'page': page}))
        return paths

renderers = [TalksRenderer, ]
