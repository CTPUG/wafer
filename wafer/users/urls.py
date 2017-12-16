from django.conf.urls import include, url
from rest_framework import routers

from wafer.users.views import (UsersView, ProfileView, EditProfileView,
                               EditUserView, UserViewSet)


router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    url(r'^$', UsersView.as_view(),
        name='wafer_users'),
    url(r'^api/', include(router.urls)),
    url(r'^page/(?P<page>\d+)/$', UsersView.as_view(),
        name='wafer_users_page'),
    url(r'^(?P<username>[\w.@+-]+)/$', ProfileView.as_view(),
        name='wafer_user_profile'),
    url(r'^(?P<username>[\w.@+-]+)/edit/$', EditUserView.as_view(),
        name='wafer_user_edit'),
    url(r'^(?P<username>[\w.@+-]+)/edit_profile/$',
        EditProfileView.as_view(),
        name='wafer_user_edit_profile'),
]
