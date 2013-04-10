from django.conf.urls.defaults import patterns, url

from wafer.conf_registration.views import (RegistrationCancel,
        RegistrationUpdate, RegistrationCreate, RegistrationView,
        AttendeeCreate, AttendeeUpdate, AttendeeView, AttendeeDelete)

urlpatterns = patterns(
    '',
    url(r'^new/$', RegistrationCreate.as_view(),
        name='wafer_registration_submit'),
    url(r'^(?P<pk>\d+)/$', RegistrationView.as_view(),
        name='wafer_registration'),
    url(r'^(?P<pk>\d+)/edit/$', RegistrationUpdate.as_view(),
        name='wafer_registration_edit'),
    url(r'^(?P<pk>\d+)/cancel/$', RegistrationCancel.as_view(),
        name='wafer_registration_cancel'),
    url(r'^attendee/new/$', AttendeeCreate.as_view(),
        name='wafer_attendee_submit'),
    url(r'^attendee/(?P<pk>\d+)/$', AttendeeView.as_view(),
        name='wafer_attendee'),
    url(r'attendee/^(?P<pk>\d+)/edit/$', AttendeeUpdate.as_view(),
        name='wafer_attendee_edit'),
    url(r'^attendee/(?P<pk>\d+)/delete/$', AttendeeDelete.as_view(),
        name='wafer_attendee_delete'),
)
