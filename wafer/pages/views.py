from django.http import Http404
from django.views.generic import DetailView

from wafer.pages.models import Page


class ShowPage(DetailView):
    template_name = 'wafer.pages/page.html'
    model = Page


def slug(request, url):
    """Look up a page by url (which is a tree of slugs"""
    page = None
    for slug in url.split('/'):
        try:
            page = Page.objects.get(slug=slug, parent=page)
        except Page.DoesNotExist:
            raise Http404
    return ShowPage.as_view()(request, pk=page.id)
