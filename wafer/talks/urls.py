from django.conf.urls import patterns, url

from wafer.talks.views import (
    TalkCreate, TalkDelete, TalkUpdate, TalkView, UsersTalks)

urlpatterns = patterns(
    '',
    url(r'^$', UsersTalks.as_view(), name='wafer_users_talks'),
    url(r'^page/(?P<page>\d+)$', UsersTalks.as_view(),
        name='wafer_users_talks_page'),
    url(r'^new/$', TalkCreate.as_view(), name='wafer_talk_submit'),
    url(r'^(?P<pk>\d+)/$', TalkView.as_view(), name='wafer_talk'),
    url(r'^(?P<pk>\d+)/edit/$', TalkUpdate.as_view(),
        name='wafer_talk_edit'),
    url(r'^(?P<pk>\d+)/delete/$', TalkDelete.as_view(),
        name='wafer_talk_delete'),
)
