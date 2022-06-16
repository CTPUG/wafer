from django.urls import include, re_path

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
    re_path(r'^claim/$', ClaimView.as_view(), name='wafer_ticket_claim'),
    re_path(r'^zapier_guest_hook/$', zapier_guest_hook),
    re_path(r'^zapier_cancel_hook/$', zapier_cancel_hook),
    re_path(r'^api/', include(router.urls)),
]
