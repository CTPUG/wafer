import re
import json
from uuid import uuid4

import requests

from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.sites.models import get_current_site
from django.core.files.base import ContentFile

from wafer.models import AttendeeRegistration
from wafer.utils import normalize_unicode
from wafer import constants


class Invoice(models.Model):

    invoice_id = models.CharField(max_length=32, editable=False,
                                  default=lambda: uuid4().hex)
    invoice_paid = models.BooleanField(default=False)
    invoice_pdf = models.FileField(upload_to='invoices', null=True,
                                   editable=False)
    # invoice_billable_params is JSON encoded
    invoice_billable_params = models.TextField(null=True, editable=False)

    attendees = models.ManyToManyField(AttendeeRegistration)

    def payment_reference(self):
        initial = self.name[0] if self.name else u''
        ref = u"PYCON: %s%s" % (initial.upper(), self.surname.upper())
        return normalize_unicode(ref)

    def invoice_url(self):
        site = get_current_site(None)
        path = reverse('attendee_invoice', args=(self.invoice_id,))
        return "http://%s%s" % (site.domain, path)

    def invoice_pdf_filename(self):
        filename = u"%s-%s-invoice.pdf" % (self.name, self.surname)
        return normalize_unicode(filename).lower()

    def get_invoice_pdf(self):
        self.invoice_pdf.open("b")
        try:
            return self.invoice_pdf.name, self.invoice_pdf.read()
        except:
            self.invoice_pdf.close()

    def generate_invoice_pdf(self, reg_kind=None, reg_price=None):
        """Generate PDF data by calling billable.me.

        :param str reg_kind:
            Override the string used to describe the kind of
            registration.
        :param int reg_price:
            Override the price of the registration.
        """
        billable_me_url = "http://billable.me/pdf/"
        params = {
            'kind': 'INVOICE',
            'company_name': 'PyConZA 2012',
            'company_info': (
                'Praekelt Foundation\n'
                'za.pycon.org | praekeltfoundation.org\n'
                'team@za.pycon.org | accounts@praekelt.com\n'
            ),
            'invoice_number_label': 'Invoice #',
            'invoice_date_label': 'Date',
            'description_label': 'Item & Description',
            'quantity_label': 'Quantity',
            'price_label': 'Price',
            'subtotal_label': 'Subtotal',
            'tax_name': 'VAT',
            'tax_percentage': '',
            'total_label': 'Total',
            'currency_symbol': 'R',
            'notes_a': '',
            'notes_b': '\nCreated with Billable.me',
        }

        params['notes_a'] = (
            "Pay by EFT to:\n"
            "\n"
            "Account number: 9275706696\n"
            "Branch code: 632005\n"
            "Account name: PyCon Conference\n"
            "Bank: ABSA\n"
            "Reference: %(reference)s\n"
        ) % {
            'reference': self.payment_reference(),
        }

        reg_desc = dict(constants.REGISTRATION_TYPES)[self.registration_type]
        match = re.match(r"(?P<kind>.*) \(R(?P<price>\d+)\)", reg_desc)
        if reg_kind is None:
            reg_kind = match.group('kind')
        if reg_price is None:
            reg_price = int(match.group('price'))

        params['invoice_number'] = str(self.pk)
        params['invoice_date'] = self.timestamp.date().isoformat()

        params['recipient_info'] = (
            u"%(name)s %(surname)s\n"
            u"%(email)s\n"
        ) % {
            "name": self.name,
            "surname": self.surname,
            "email": self.email,
        }

        params['items.0.description'] = ('PyConZA 2012 registration (%s)'
                                         % reg_kind)
        params['items.0.quantity'] = '1'
        params['items.0.price'] = "%.2f" % reg_price

        params['subtotal'] = "%.2f" % reg_price
        params['tax_amount'] = "N/A"
        params['total'] = "%.2f" % reg_price
        params = dict((k, v.encode('utf-8')) for k, v in params.iteritems())

        response = requests.post(billable_me_url, data=params)
        pdf_data = response.content

        self.invoice_billable_params = json.dumps(params)
        self.invoice_pdf.save(self.invoice_pdf_filename(),
                              ContentFile(pdf_data))
