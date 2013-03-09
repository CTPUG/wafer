from django.contrib import admin
from django import forms
from wafer.invoices.models import Invoice, InvoiceTemplate


class InvoiceAdminForm(forms.ModelForm):
    class Meta:
        model = Invoice

    def __init__(self, initial=None, **kwargs):
        initial = Invoice.default_params()
        super(InvoiceAdminForm, self).__init__(initial=initial, **kwargs)


class InvoiceAdmin(admin.ModelAdmin):
    form = InvoiceAdminForm
    search_fields = ('pk', 'recipient_info')
    readonly_fields = ('pdf',)

admin.site.register(Invoice, InvoiceAdmin)


class InvoiceTemplateAdmin(admin.ModelAdmin):
    list_display = ('reference_template', 'company_name',
                    'currency_symbol', 'default')
    list_editable = ('default',)

admin.site.register(InvoiceTemplate, InvoiceTemplateAdmin)
