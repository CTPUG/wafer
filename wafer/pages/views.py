from django.http import Http404, HttpResponseRedirect
from django.views.generic import DetailView, TemplateView

from wafer.pages.models import Page


class ShowPage(DetailView):
    template_name = 'wafer.pages/page.html'
    model = Page


def slug(request, url):
    """Look up a page by url (which is a tree of slugs)"""
    if url in ('index', 'index.html'):
        return HttpResponseRedirect('/')

    page = None
    for slug in url.split('/'):
        if not slug:
            continue
        try:
            page = Page.objects.get(slug=slug, parent=page)
        except Page.DoesNotExist:
            raise Http404

    if page is None:
        try:
            page = Page.objects.get(slug='index')
        except Page.DoesNotExist:
            return TemplateView.as_view(
                template_name='wafer/index.html')(request)

    return ShowPage.as_view()(request, pk=page.id)
