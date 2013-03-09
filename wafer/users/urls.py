from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
      url(r'^([\w.@+-]+)/$', 'wafer.users.views.profile',
          name='wafer_user_profile'),
)
