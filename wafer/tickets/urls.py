from django.conf.urls import include, url

from rest_framework import routers

from wafer.tickets.views import (
    ClaimView,
    TicketTypesViewSet,
    TicketsViewSet,
    zapier_cancel_hook,
    zapier_guest_hook,
)

router = routers.DefaultRouter()
router.register(r'tickets', TicketsViewSet)
router.register(r'tickettypes', TicketTypesViewSet)

urlpatterns = [
    url(r'^claim/$', ClaimView.as_view(), name='wafer_ticket_claim'),
    url(r'^zapier_guest_hook/$', zapier_guest_hook),
    url(r'^zapier_cancel_hook/$', zapier_cancel_hook),
    url(r'^api/', include(router.urls)),
]
