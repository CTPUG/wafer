from django_medusa.renderers import StaticSiteRenderer
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.conf import settings

from wafer.users.views import UsersView



class UserRenderer(StaticSiteRenderer):
    def get_paths(self):
        paths = []
        if settings.WAFER_PUBLIC_ATTENDEE_LIST:
            paths.append("/users/")

        items = get_user_model().objects.all()
        for item in items:
            if not settings.WAFER_PUBLIC_ATTENDEE_LIST:
                # We need to filter out the non-publically
                # accessible paths from the static site
                if not item.userprofile.accepted_talks().exists():
                    continue
            paths.append(reverse('wafer_user_profile',
                                 kwargs={'username': item.username}))
        if settings.WAFER_PUBLIC_ATTENDEE_LIST:
            view = UsersView()
            queryset = view.get_queryset()
            paginator = view.get_paginator(queryset,
                                           view.get_paginate_by(queryset))
            for page in paginator.page_range:
                paths.append(reverse('wafer_users_page',
                                     kwargs={'page': page}))
        return paths

renderers = [UserRenderer, ]
