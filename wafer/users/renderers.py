from django_medusa.renderers import StaticSiteRenderer
from django.core.urlresolvers import reverse

from wafer.users.views import UsersView
from django.contrib.auth.models import User


class UserRenderer(StaticSiteRenderer):
    def get_paths(self):
        paths = ["/users/", ]

        items = User.objects.all()
        for item in items:
            paths.append(item.get_absolute_url())

        view = UsersView()
        queryset = view.get_queryset()
        paginator = view.get_paginator(queryset,
                                       view.get_paginate_by(queryset))
        for page in paginator.page_range:
            paths.append(reverse('wafer_users_page',
                                 kwargs={'page': page}))
        return paths

renderers = [UserRenderer, ]
