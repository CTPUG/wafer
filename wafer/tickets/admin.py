from django.contrib import admin

from wafer.tickets.models import Ticket, TicketType

admin.site.register(Ticket)
admin.site.register(TicketType)
