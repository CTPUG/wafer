from django.urls import re_path, include
from rest_framework_extensions import routers

from wafer.talks.views import (
    Speakers, ReviewViewSet, TalkCreate, TalkReview, TalkTypesView, TalkUpdate,
    TalkUrlsViewSet, TalkView, TalkWithdraw, TalksViewSet, TracksView,
    UsersTalks)

router = routers.ExtendedSimpleRouter()

talks_router = router.register(r'talks', TalksViewSet)
talks_router.register(
    r'urls', TalkUrlsViewSet, basename='talks-urls',
    parents_query_lookups=['talk'])
talks_router.register(
    r'reviews', ReviewViewSet, basename='talks-reviews',
    parents_query_lookups=['talk'])

urlpatterns = [
    re_path(r'^$', UsersTalks.as_view(), name='wafer_users_talks'),
    re_path(r'^page/(?P<page>\d+)/$', UsersTalks.as_view(),
        name='wafer_users_talks_page'),
    re_path(r'^new/$', TalkCreate.as_view(), name='wafer_talk_submit'),
    re_path(r'^(?P<pk>\d+)(?:-(?P<slug>[\w-]*))?/$', TalkView.as_view(),
        name='wafer_talk'),
    re_path(r'^(?P<pk>\d+)/edit/$', TalkUpdate.as_view(),
        name='wafer_talk_edit'),
    re_path(r'^(?P<pk>\d+)/review/$', TalkReview.as_view(),
        name='wafer_talk_review'),
    re_path(r'^(?P<pk>\d+)/withdraw/$', TalkWithdraw.as_view(),
        name='wafer_talk_withdraw'),
    re_path(r'^speakers/$', Speakers.as_view(), name='wafer_talks_speakers'),
    re_path(r'^tracks/', TracksView.as_view(), name='wafer_talk_tracks'),
    re_path(r'^types/', TalkTypesView.as_view(), name='wafer_talk_types'),
    re_path(r'^api/', include(router.urls)),
]
