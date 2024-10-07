from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _
from reversion.admin import VersionAdmin

from wafer.tickets.models import Ticket, TicketType, TicketTypeTag


class ClaimedFilter(admin.SimpleListFilter):
    title = _('ticket claimed')
    parameter_name = 'claimed'

    def lookups(self, request, model_admins):
        return (
            ('yes', _('Ticket has been claimed')),
            ('no', _('Ticket is unclaimed'))
            )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(user__isnull=False)
        elif self.value() == 'no':
            return queryset.filter(user__isnull=True)
        return queryset

class TicketTypeTagAdmin(VersionAdmin):
    pass


# We don't use the versioned admin here, as these are usually created and
# updated by external triggers and we don't currently version that
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_tags', 'get_ticket_count')
    list_filter = ('tags',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            ticket_count_annotation=models.Count('ticket', distinct=True),
        )
        return qs

    def get_ticket_count(self, obj):
        return obj.ticket_count_annotation

    get_ticket_count.short_description = 'total purchased'
    get_ticket_count.admin_order_field = 'ticket_count_annotation'


class TicketAdmin(admin.ModelAdmin):
    list_filter = (ClaimedFilter, 'type')


admin.site.register(Ticket, TicketAdmin)
admin.site.register(TicketType, TicketTypeAdmin)
admin.site.register(TicketTypeTag, TicketTypeTagAdmin)
