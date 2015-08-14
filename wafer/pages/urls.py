from django.conf.urls import patterns, url
from django.core.urlresolvers import get_script_prefix
from django.views.generic import RedirectView

urlpatterns = patterns(
    'wafer.pages.views',
    url('^index(?:\.html)?$', RedirectView.as_view(
        url=get_script_prefix(), query_string=True)),
    url(r'^(.*)$', 'slug', name='wafer_page'),
)
