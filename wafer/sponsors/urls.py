from django.conf.urls import patterns, url

from wafer.sponsors.views import (
    ShowSponsors, SponsorView, ShowPackages)

urlpatterns = patterns(
    '',
    url(r'^$', ShowSponsors.as_view(),
        name='wafer_sponsors'),
    url(r'^(?P<pk>\d+)/$', SponsorView.as_view(), name='wafer_sponsor'),
    url(r'^packages/$', ShowPackages.as_view(),
        name='wafer_sponsorship_packages'),

)
