from django.conf.urls.defaults import include, patterns, url
from django.views.generic import RedirectView, TemplateView

urlpatterns = patterns('',
    url(r'^$',
        TemplateView.as_view(template_name='wafer/index.html'),
        name='index'),

    url(r'^index.html$',
        RedirectView.as_view(url='/'),
        name='index_redirect'),

    (r'^accounts/', include('registration.backends.default.urls')),
)
