from django.conf.urls import patterns, url
from django.views.generic import RedirectView

urlpatterns = patterns(
    'wafer.pages.views',
    url('^index(?:\.html)?$', RedirectView.as_view(url='/')),
    url(r'^(.*)$', 'slug', name='wafer_page'),
)
