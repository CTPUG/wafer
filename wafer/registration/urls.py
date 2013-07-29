from django.conf.urls import include, patterns, url
from django.views.generic import TemplateView
from registration.backends.default.views import ActivationView, RegistrationView


urlpatterns = patterns(
    'wafer.registration.views',
    url(r'^profile/$', 'redirect_profile'),

    url(r'^github-login/$', 'github_login'),

    # registration.backends.default.urls, but Django 1.5 compatible
    url(r'^activate/complete/$',
        TemplateView.as_view(
            template_name='registration/activation_complete.html'
        ), name='registration_activation_complete'),
    url(r'^activate/(?P<activation_key>\w+)/$',
        ActivationView.as_view(
            template_name='registration/activate.html'
        ), name='registration_activate'),
    url(r'^register/$',
        RegistrationView.as_view(
            template_name='registration/registration_form.html'
        ),
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
