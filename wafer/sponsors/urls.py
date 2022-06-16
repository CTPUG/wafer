from django.urls import re_path, include
from rest_framework import routers

from wafer.sponsors.views import (
    ShowSponsors, SponsorView, ShowPackages, SponsorViewSet, PackageViewSet)


router = routers.DefaultRouter()
router.register(r'sponsors', SponsorViewSet)
router.register(r'packages', PackageViewSet)

urlpatterns = [
    re_path(r'^$', ShowSponsors.as_view(),
        name='wafer_sponsors'),
    re_path(r'^(?P<pk>\d+)/$', SponsorView.as_view(), name='wafer_sponsor'),
    re_path(r'^packages/$', ShowPackages.as_view(),
        name='wafer_sponsorship_packages'),
    re_path(r'^api/', include(router.urls)),
]
