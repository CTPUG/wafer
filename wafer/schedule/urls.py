from django.conf.urls import include, url
from rest_framework import routers


from wafer.schedule.views import (
    CurrentView, ScheduleView, ScheduleItemViewSet, ScheduleXmlView,
    VenueView, ICalView)

router = routers.DefaultRouter()
router.register(r'scheduleitems', ScheduleItemViewSet)

urlpatterns = [
    url(r'^$', ScheduleView.as_view(), name='wafer_full_schedule'),
    url(r'^venue/(?P<pk>\d+)/$', VenueView.as_view(), name='wafer_venue'),
    url(r'^current/$', CurrentView.as_view(), name='wafer_current'),
    url(r'^pentabarf\.xml$', ScheduleXmlView.as_view(),
        name='wafer_pentabarf_xml'),
    url(r'^schedule\.ics$', ICalView.as_view(), name="schedule.ics"),
    url(r'^api/', include(router.urls)),
]
