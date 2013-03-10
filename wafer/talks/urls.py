from django.conf.urls.defaults import patterns, url

from wafer.talks.views import TalkCreate

urlpatterns = patterns('',
      url(r'^new/$', TalkCreate.as_view(), name='talk_submit'),
)
