from django.conf.urls.defaults import include, patterns, url
from django.views.generic import TemplateView
from registration.views import activate, register

from wafer.registration.views import redirect_profile


backend = 'wafer.registration.backends.WaferBackend'
urlpatterns = patterns('',
    url(r'^profile/$', redirect_profile),

    # registration.backends.default.urls, modified with our backend
    url(r'^activate/complete/$',
        TemplateView.as_view(
            template_name='registration/activation_complete.html'
        ), name='registration_activation_complete'),
    url(r'^activate/(?P<activation_key>\w+)/$',
        activate, {'backend': backend},
        name='registration_activate'),
    url(r'^register/$',
        register, {'backend': backend},
        name='registration_register'),
    url(r'^register/complete/$',
        TemplateView.as_view(
            template_name='registration/registration_complete.html'
        ), name='registration_complete'),
    url(r'^register/closed/$',
        TemplateView.as_view(
            template_name='registration/registration_closed.html'
        ), name='registration_disallowed'),
    url(r'', include('registration.auth_urls')),
)
