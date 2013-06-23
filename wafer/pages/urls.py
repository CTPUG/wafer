from django.conf.urls import patterns, url

from wafer.pages.views import ShowPage

urlpatterns = patterns(
    '',
    url(r'^(?P<pk>\d+)$', ShowPage.as_view(),
        name='wafer_page'),
)
