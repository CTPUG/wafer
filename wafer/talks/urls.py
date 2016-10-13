from django.conf.urls import url, include
from rest_framework_extensions import routers

from wafer.talks.views import (
    Speakers, TalkCreate, TalkDelete, TalkUpdate, TalkView, UsersTalks,
    TalksViewSet, TalkUrlsViewSet)

router = routers.ExtendedSimpleRouter()

talks_router = router.register(r'talks', TalksViewSet)
talks_router.register(
    r'urls', TalkUrlsViewSet, base_name='talks-urls',
    parents_query_lookups=['talk'])

urlpatterns = [
    url(r'^$', UsersTalks.as_view(), name='wafer_users_talks'),
    url(r'^page/(?P<page>\d+)/$', UsersTalks.as_view(),
        name='wafer_users_talks_page'),
    url(r'^new/$', TalkCreate.as_view(), name='wafer_talk_submit'),
    url(r'^(?P<pk>\d+)/$', TalkView.as_view(), name='wafer_talk'),
    url(r'^(?P<pk>\d+)/edit/$', TalkUpdate.as_view(),
        name='wafer_talk_edit'),
    url(r'^(?P<pk>\d+)/delete/$', TalkDelete.as_view(),
        name='wafer_talk_delete'),
    url(r'^speakers/$', Speakers.as_view(), name='wafer_talks_speakers'),
    url(r'^api/', include(router.urls)),
]
