from django.conf.urls import url, include
from rest_framework import routers

from wafer.sponsors.views import (
    ShowSponsors, SponsorView, ShowPackages, SponsorViewSet, PackageViewSet)


router = routers.DefaultRouter()
router.register(r'sponsors', SponsorViewSet)
router.register(r'packages', PackageViewSet)

urlpatterns = [
    url(r'^$', ShowSponsors.as_view(),
        name='wafer_sponsors'),
    url(r'^(?P<pk>\d+)/$', SponsorView.as_view(), name='wafer_sponsor'),
    url(r'^packages/$', ShowPackages.as_view(),
        name='wafer_sponsorship_packages'),
    url(r'^api/', include(router.urls)),
]
