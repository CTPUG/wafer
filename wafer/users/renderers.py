from django_medusa.renderers import StaticSiteRenderer
from django.contrib.auth.models import User


class UserRenderer(StaticSiteRenderer):
    def get_paths(self):
        paths = ["/users/", ]

        items = User.objects.all()
        for item in items:
            paths.append(item.get_absolute_url())
        return paths

renderers = [UserRenderer, ]
