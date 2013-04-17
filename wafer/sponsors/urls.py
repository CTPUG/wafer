from django.conf.urls.defaults import patterns, url

from wafer.sponsors.views import (
    ShowSponsors, ShowPackages)

urlpatterns = patterns(
    '',
    url(r'^$', ShowSponsors.as_view(),
        name='wafer_sponsors'),
    url(r'^packages/$', ShowPackages.as_view(),
        name='wafer_sponsorship_packages'),
)
