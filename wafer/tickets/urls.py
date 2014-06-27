from django.conf.urls import patterns, url


urlpatterns = patterns(
    'wafer.tickets.views',
    url(r'^claim/$', 'claim', name='wafer_ticket_claim'),
    url(r'^quicket_hook/$', 'quicket_hook'),
)
