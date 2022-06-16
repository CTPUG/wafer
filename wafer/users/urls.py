from django.urls import include, re_path
from rest_framework import routers

from wafer.users.views import (UsersView, ProfileView, EditProfileView,
                               EditUserView, UserViewSet)


router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    re_path(r'^$', UsersView.as_view(),
        name='wafer_users'),
    re_path(r'^api/', include(router.urls)),
    re_path(r'^page/(?P<page>\d+)/$', UsersView.as_view(),
        name='wafer_users_page'),
    re_path(r'^(?P<username>[\w.@+-]+)/$', ProfileView.as_view(),
        name='wafer_user_profile'),
    re_path(r'^(?P<username>[\w.@+-]+)/edit/$', EditUserView.as_view(),
        name='wafer_user_edit'),
    re_path(r'^(?P<username>[\w.@+-]+)/edit_profile/$',
        EditProfileView.as_view(),
        name='wafer_user_edit_profile'),
]
