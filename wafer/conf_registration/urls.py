from django.conf.urls import patterns, url

from wafer.conf_registration.views import (AttendeeCreate, AttendeeUpdate,
        AttendeeView, AttendeeDelete, AllAttendeeView)

urlpatterns = patterns(
    '',
    url(r'^new/$', AttendeeCreate.as_view(),
        name='wafer_registration_submit'),
    url(r'^(?P<pk>\d+)/$', AttendeeView.as_view(),
        name='wafer_registration'),
    url(r'^(?P<pk>\d+)/all/$', AllAttendeeView.as_view(),
        name='wafer_all_registration'),
    url(r'^(?P<pk>\d+)/edit/$', AttendeeUpdate.as_view(),
        name='wafer_registration_edit'),
    url(r'^(?P<pk>\d+)/cancel/$', AttendeeDelete.as_view(),
        name='wafer_registration_cancel'),
)
