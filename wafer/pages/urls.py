from django.conf.urls import include, url
from django.urls import get_script_prefix
from django.views.generic import RedirectView

from rest_framework import routers

from wafer.pages.views import PageViewSet, slug

router = routers.DefaultRouter()
router.register(r'pages', PageViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url('^index(?:\.html)?/?$', RedirectView.as_view(
        url=get_script_prefix(), permanent=True, query_string=True)),
    url(r'^(?:(.+)/)?$', slug, name='wafer_page'),
]
