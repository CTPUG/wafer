from django.contrib import admin
from wafer.invoices.models import Invoice, InvoiceTemplate


class InvoiceAdmin(admin.ModelAdmin):
    search_fields = ('pk', 'recipient_info')
    readonly_fields = ('pdf')

admin.site.register(Invoice, InvoiceAdmin)


class InvoiceTemplateAdmin(admin.ModelAdmin):
    pass

admin.site.register(InvoiceTemplate, InvoiceTemplateAdmin)
