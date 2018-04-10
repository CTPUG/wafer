from django.conf.urls import include, url

from wafer.registration.views import debian_login, github_login, redirect_profile


urlpatterns = [
    url(r'^profile/$', redirect_profile),

    url(r'^github-login/$', github_login),
    url(r'^debian-login/$', debian_login),

    url(r'', include('registration.backends.default.urls')),
    url(r'', include('registration.auth_urls')),
]
