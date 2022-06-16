from django.urls import include, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    re_path(r'^accounts/', include('wafer.registration.urls')),
    re_path(r'^users/', include('wafer.users.urls')),
    re_path(r'^talks/', include('wafer.talks.urls')),
    re_path(r'^sponsors/', include('wafer.sponsors.urls')),
    re_path(r'^pages/', include('wafer.pages.urls')),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^markitup/', include('markitup.urls')),
    re_path(r'^schedule/', include('wafer.schedule.urls')),
    re_path(r'^tickets/', include('wafer.tickets.urls')),
    re_path(r'^kv/', include('wafer.kv.urls')),
]

# Serve media
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Pages occupy the entire URL space, and must come last
urlpatterns.append(re_path(r'', include('wafer.pages.urls')))
