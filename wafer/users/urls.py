from django.conf.urls.defaults import patterns, url

from wafer.users.views import ProfileView

urlpatterns = patterns('',
      url(r'^(?P<username>[\w.@+-]+)/$', ProfileView.as_view(),
          name='wafer_user_profile'),
)
