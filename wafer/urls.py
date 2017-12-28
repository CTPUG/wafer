from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r'^accounts/', include('wafer.registration.urls')),
    url(r'^users/', include('wafer.users.urls')),
    url(r'^talks/', include('wafer.talks.urls')),
    url(r'^sponsors/', include('wafer.sponsors.urls')),
    url(r'^pages/', include('wafer.pages.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^markitup/', include('markitup.urls')),
    url(r'^schedule/', include('wafer.schedule.urls')),
    url(r'^tickets/', include('wafer.tickets.urls')),
    url(r'^kv/', include('wafer.kv.urls')),
]

# Serve media
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Pages occupy the entire URL space, and must come last
urlpatterns.append(url(r'', include('wafer.pages.urls')))
