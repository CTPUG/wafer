from django.conf.urls import patterns, url

from wafer.users.views import (UsersView, ProfileView, EditProfileView,
                               EditUserView)

urlpatterns = patterns(
    '',
    url(r'^$', UsersView.as_view(),
        name='wafer_users'),
    url(r'^page/(?P<page>\d+)$', UsersView.as_view(),
        name='wafer_users_page'),
    url(r'^(?P<username>[\w.@+-]+)/$', ProfileView.as_view(),
        name='wafer_user_profile'),
    url(r'^(?P<username>[\w.@+-]+)/edit/$', EditUserView.as_view(),
        name='wafer_user_edit'),
    url(r'^(?P<username>[\w.@+-]+)/edit_profile/$',
        EditProfileView.as_view(),
        name='wafer_user_edit_profile'),
)
