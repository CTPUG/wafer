from django.urls import include, re_path

from wafer.registration.views import (
    github_login, gitlab_login, redirect_profile)


urlpatterns = [
    re_path(r'^profile/$', redirect_profile),

    re_path(r'^github-login/$', github_login),
    re_path(r'^gitlab-login/$', gitlab_login),

    re_path(r'', include('registration.backends.default.urls')),
    re_path(r'', include('registration.auth_urls')),
]
