from django.conf.urls import include, url

from rest_framework import routers

from wafer.kv.views import KeyValueViewSet

router = routers.DefaultRouter()
router.register(r'kv', KeyValueViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
]
