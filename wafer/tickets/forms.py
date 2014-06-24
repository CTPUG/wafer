from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError

from wafer.tickets.models import Ticket


class TicketForm(forms.Form):

    barcode = forms.fields.IntegerField(label='Ticket barcode')

    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Claim')))

    def clean_barcode(self):
        try:
            ticket = Ticket.objects.get(barcode=self.cleaned_data['barcode'])
        except Ticket.DoesNotExist:
            raise ValidationError(_(
                "There is no ticket with that barcode that's we're aware of "
                "being sold, yet. Please check it, and if correct, contact us."
            ))
        if ticket.user:
            raise ValidationError(_(
                "This ticket has already been claimed, by another user."))
        return self.cleaned_data['barcode']
