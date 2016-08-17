from django.conf.urls import patterns, url, include
from django.core.urlresolvers import get_script_prefix
from django.views.generic import RedirectView
from rest_framework import routers

from wafer.pages.views import PageViewSet

router = routers.DefaultRouter()
router.register(r'pages', PageViewSet)

urlpatterns = patterns(
    'wafer.pages.views',
    url(r'^api/', include(router.urls)),
    url('^index(?:\.html)?/?$', RedirectView.as_view(
        url=get_script_prefix(), query_string=True)),
    url(r'^(?:(.+)/)?$', 'slug', name='wafer_page'),
)
