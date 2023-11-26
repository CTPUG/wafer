from django.urls import include, re_path
from rest_framework import routers


from wafer.schedule.views import (
    CurrentView, ScheduleView, ScheduleItemViewSet, ScheduleXmlView,
    VenueView, ICalView, JsonDataView, get_validation_info)

router = routers.DefaultRouter()
router.register(r'scheduleitems', ScheduleItemViewSet)

urlpatterns = [
    re_path(r'^$', ScheduleView.as_view(), name='wafer_full_schedule'),
    re_path(r'^venue/(?P<pk>\d+)/$', VenueView.as_view(), name='wafer_venue'),
    re_path(r'^current/$', CurrentView.as_view(), name='wafer_current'),
    re_path(r'^pentabarf\.xml$', ScheduleXmlView.as_view(),
        name='wafer_pentabarf_xml'),
    re_path(r'^schedule\.ics$', ICalView.as_view(), name="schedule.ics"),
    re_path(r'^schedule\.json$', JsonDataView.as_view(), name="schedule.json"),
    re_path(r'^api/validate', get_validation_info),
    re_path(r'^api/', include(router.urls)),
]
