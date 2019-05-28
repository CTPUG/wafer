from django.conf.urls import url, include
from rest_framework_extensions import routers

from wafer.talks.views import (
    Speakers, TalkCreate, TalkReview, TalkTypesView, TalkUpdate,
    TalkUrlsViewSet, TalkView, TalkWithdraw, TalksViewSet, TracksView,
    UsersTalks)

router = routers.ExtendedSimpleRouter()

# FIXME: Change base_name when we drop python 2 and move to drf-extensions 0.5
talks_router = router.register(r'talks', TalksViewSet)
talks_router.register(
    r'urls', TalkUrlsViewSet, base_name='talks-urls',
    parents_query_lookups=['talk'])

urlpatterns = [
    url(r'^$', UsersTalks.as_view(), name='wafer_users_talks'),
    url(r'^page/(?P<page>\d+)/$', UsersTalks.as_view(),
        name='wafer_users_talks_page'),
    url(r'^new/$', TalkCreate.as_view(), name='wafer_talk_submit'),
    url(r'^(?P<pk>\d+)(?:-(?P<slug>[\w-]+))?/$', TalkView.as_view(),
        name='wafer_talk'),
    url(r'^(?P<pk>\d+)/edit/$', TalkUpdate.as_view(),
        name='wafer_talk_edit'),
    url(r'^(?P<pk>\d+)/review/$', TalkReview.as_view(),
        name='wafer_talk_review'),
    url(r'^(?P<pk>\d+)/withdraw/$', TalkWithdraw.as_view(),
        name='wafer_talk_withdraw'),
    url(r'^speakers/$', Speakers.as_view(), name='wafer_talks_speakers'),
    url(r'^tracks/', TracksView.as_view(), name='wafer_talk_tracks'),
    url(r'^types/', TalkTypesView.as_view(), name='wafer_talk_types'),
    url(r'^api/', include(router.urls)),
]
