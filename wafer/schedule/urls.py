from django.conf.urls import patterns, url

from wafer.schedule.views import (VenueView, ScheduleView, CurrentView,
                                  ScheduleXmlView)

urlpatterns = patterns(
    '',
    url(r'^$', ScheduleView.as_view(), name='wafer_full_schedule'),
    url(r'^venue/(?P<pk>\d+)/$', VenueView.as_view(), name='wafer_venue'),
    url(r'^current/$', CurrentView.as_view(), name='wafer_current'),
    url(r'^pentabarf\.xml$', ScheduleXmlView.as_view(),
        name='wafer_pentabarf_xml'),
)
