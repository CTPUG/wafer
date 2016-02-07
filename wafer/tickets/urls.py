from django.conf.urls import patterns, url
from wafer.tickets.views import ClaimView


urlpatterns = patterns(
    'wafer.tickets.views',
    url(r'^claim/$', ClaimView.as_view(), name='wafer_ticket_claim'),
    url(r'^quicket_hook/$', 'quicket_hook'),
)
