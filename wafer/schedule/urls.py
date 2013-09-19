from django.conf.urls.defaults import patterns, url

from wafer.schedule.views import VenueView, ScheduleView

urlpatterns = patterns(
    '',
    url(r'^/venue/(?<P<pk>\d+)$', VenueView.as_view(),
        name='wafer_venue'),
    url(r'^/schedule$', ScheduleView.as_view(),
        name='wafer_full_schedule'),
)
