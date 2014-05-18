from django.conf.urls import patterns, url

from wafer.schedule.views import VenueView, ScheduleView

urlpatterns = patterns(
    '',
    url(r'^$', ScheduleView.as_view(), name='wafer_full_schedule'),
    url(r'^/venue/(?P<pk>\d+)/$', VenueView.as_view(), name='wafer_venue'),
)
