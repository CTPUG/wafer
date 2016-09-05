from django.conf.urls import patterns, url, include
from rest_framework import routers

from wafer.pages.views import PageViewSet

router = routers.DefaultRouter()
router.register(r'pages', PageViewSet)

urlpatterns = patterns(
    'wafer.pages.views',
    url(r'^api/', include(router.urls)),
    url(r'^(?:(.+)/)?$', 'slug', name='wafer_page'),
)
