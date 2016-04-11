from django.conf.urls import patterns, url, include

from rest_framework import routers

from wafer.kv.views import KeyValueViewSet

router = routers.DefaultRouter()
router.register(r'kv', KeyValueViewSet)

urlpatterns = patterns(
    '',
    url(r'^api/', include(router.urls)),
)
