from django.conf.urls.defaults import patterns, url

from wafer.conf_registration.views import (RegistrationCancel,
        RegistrationUpdate, RegistrationCreate, RegistrationView)

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
)
