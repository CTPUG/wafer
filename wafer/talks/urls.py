from django.conf.urls.defaults import patterns, url

from wafer.talks.views import TalkCreate, TalkDelete, TalkUpdate, TalkView

urlpatterns = patterns('',
      url(r'^new/$', TalkCreate.as_view(), name='wafer_talk_submit'),
      url(r'^(?P<pk>\d+)/$', TalkView.as_view(), name='wafer_talk'),
      url(r'^(?P<pk>\d+)/edit/$', TalkUpdate.as_view(),
          name='wafer_talk_edit'),
      url(r'^(?P<pk>\d+)/delete/$', TalkDelete.as_view(),
          name='wafer_talk_delete'),
)
