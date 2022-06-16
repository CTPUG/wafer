from django.urls import include, re_path

from rest_framework import routers

from wafer.kv.views import KeyValueViewSet

router = routers.DefaultRouter()
router.register(r'kv', KeyValueViewSet)

urlpatterns = [
    re_path(r'^api/', include(router.urls)),
]
