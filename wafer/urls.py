from django.conf.urls import include, patterns, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',

    (r'^accounts/', include('wafer.registration.urls')),
    (r'^users/', include('wafer.users.urls')),
    (r'^talks/', include('wafer.talks.urls')),
    (r'^sponsors/', include('wafer.sponsors.urls')),
    (r'^pages/', include('wafer.pages.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^markitup/', include('markitup.urls')),
    (r'^schedule/', include('wafer.schedule.urls')),
    (r'^tickets/', include('wafer.tickets.urls')),

    # Pages occupy the entire URL space, and must come last
    url(r'', include('wafer.pages.urls')),
)

# Serve media
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
