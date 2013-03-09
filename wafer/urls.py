from django.conf.urls.defaults import include, patterns, url
from django.views.generic import RedirectView, TemplateView
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$',
        TemplateView.as_view(template_name='wafer/index.html'),
        name='wafer_index'),

    url(r'^index.html$',
        RedirectView.as_view(url='/')),

    url('^contact.html', 'wafer.views.contact', name='wafer_contact'),

    (r'^accounts/', include('wafer.registration.urls')),
    (r'^users/', include('wafer.users.urls')),
    (r'^talks/', include('wafer.talks.urls')),
    (r'^admin/', include(admin.site.urls)),
)
