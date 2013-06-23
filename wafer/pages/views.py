from django.views.generic import DetailView

from wafer.pages.models import Page


class ShowPage(DetailView):
    template_name = 'wafer.pages/page.html'
    model = Page
