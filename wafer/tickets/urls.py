from django.conf.urls import patterns, url


urlpatterns = patterns(
    'wafer.tickets.views',
    url(r'^quicket_hook/$', 'quicket_hook'),
)
