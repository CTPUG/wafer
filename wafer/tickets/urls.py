from django.conf.urls import url
from wafer.tickets.views import ClaimView, zapier_cancel_hook, zapier_guest_hook


urlpatterns = [
    url(r'^claim/$', ClaimView.as_view(), name='wafer_ticket_claim'),
    url(r'^zapier_guest_hook/$', zapier_guest_hook),
    url(r'^zapier_cancel_hook/$', zapier_cancel_hook),
]

