from django.conf.urls import include, url

from wafer.registration.views import (
    github_login, gitlab_login, redirect_profile)


urlpatterns = [
    url(r'^profile/$', redirect_profile),

    url(r'^github-login/$', github_login),
    url(r'^gitlab-login/$', gitlab_login),

    url(r'', include('registration.backends.default.urls')),
    url(r'', include('registration.auth_urls')),
]
