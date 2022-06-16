from django.urls import include, re_path, get_script_prefix
from django.views.generic import RedirectView

from rest_framework import routers

from wafer.pages.views import PageViewSet, slug

router = routers.DefaultRouter()
router.register(r'pages', PageViewSet)

urlpatterns = [
    re_path(r'^api/', include(router.urls)),
    re_path(r'^index(?:\.html)?/?$', RedirectView.as_view(
        url=get_script_prefix(), permanent=True, query_string=True)),
    re_path(r'^(?:(.+)/)?$', slug, name='wafer_page'),
]
