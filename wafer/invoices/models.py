import requests

from django.db import models
from django.core.files.base import ContentFile
from django import settings

from wafer.models import AttendeeRegistration


class InvoiceTemplate(models.Model):

    DEFAULT_COMPANY_NAME = "Wafercon 20XX"
    DEFAULT_COMPANY_INFO = (
        "Wafercon Foundation\n"
        "wafercon.example.com\n"
        "team@waferconf.example.com"
    )
    DEFAULT_PAYMENT_DETAILS = (
        "Pay by EFT to:\n"
        "Account number: XXX\n"
        "Branch code: YYY\n"
        "Account name: Wafercon\n"
        "Bank: ZZZ\n"
        "Reference: %(reference)s"
    )
    DEFAULT_ADDITIONAL_NOTES = "Created with Billable.me"

    default = models.BooleanField(default=False)
    company_name = models.TextField(
        required=True, default=DEFAULT_COMPANY_NAME)
    company_info = models.TextField(
        required=True, default=DEFAULT_COMPANY_INFO)
    tax_name = models.TextField(required=True, default="VAT")
    tax_percentage = models.DecimalField(max_digits=12, decimal_places=2,
                                         null=True, default=None)
    currency_symbol = models.CharField(max_length=16, required=True,
                                       default='R')
    payment_details = models.TextField(
        required=True, default=DEFAULT_PAYMENT_DETAILS,
        help_text="You should use '%(reference)s' to include the invoice"
                  " reference.")
    additional_notes = models.TextField(
        required=True, default=DEFAULT_ADDITIONAL_NOTES)
    reference_template = models.TextField(
        required=True, default="INVOICE:%(invoice_no)s",
        help_text="You should use '%(invoice_no)s' to include the invoice"
                  " number.")


class Invoice(models.Model):

    PROVISIONAL, UNPAID, PAID, CANCELLED = (
        'provisional', 'unpaid', 'paid', 'cancelled')

    STATES = (
        (UNPAID, 'Unpaid'),
        (PAID, 'Paid'),
        (CANCELLED, 'Cancelled'),
    )

    STATIC_BILLABLEME_PARAMS = {
        'kind': 'INVOICE',
        'invoice_number_label': 'Invoice #',
        'invoice_date_label': 'Date',
        'description_label': 'Item & Description',
        'quantity_label': 'Quantity',
        'price_label': 'Price',
        'subtotal_label': 'Subtotal',
        'total_label': 'Total',
    }

    attendees = models.ManyToManyField(AttendeeRegistration)
    timestamp = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=32, choices=STATES,
                             default=PROVISIONAL)
    recipient_info = models.TextField(required=True)
    pdf = models.FileField(upload_to='invoices', null=True)

    # templated fields
    company_name = models.TextField(required=True)
    company_info = models.TextField(required=True)
    tax_name = models.TextField(required=True)
    tax_percentage = models.DecimalField(max_digits=12, decimal_places=2,
                                         null=True, required=True)
    currency_symbol = models.CharField(max_length=16, required=True)
    payment_details = models.TextField(required=True)
    additional_notes = models.TextField(required=True)
    reference_template = models.TextField(required=True)

    TEMPLATED_FIELDS = (company_name, company_info, tax_name,
                        tax_percentage, currency_symbol, payment_details,
                        additional_notes, reference_template)

    @property
    def reference(self):
        return self.reference_template % {'invoice_no': self.pk}

    @property
    def pdf_filename(self):
        return u"invoice-%s.pdf" % self.pk

    @classmethod
    def invoice_for_attendee(cls, attendee):
        templates = InvoiceTemplate.objects.filter(default=True)
        if not templates:
            template = InvoiceTemplate(default=True)
            template.save()
        else:
            template = templates[0]
        params = cls.params_from_template(template)

        recipient_info = "%s %s\n%s" % (
            attendee.name, attendee.surname,
            attendee.email,
        )

        invoice = cls(recipient_info=recipient_info,
                      attendees=[attendee],
                      **params)
        return invoice

    @classmethod
    def params_from_template(cls, template):
        params = {}
        for field in cls.TEMPLATED_FIELDS:
            params[field.name] = getattr(template, field.name)
        return params

    def get_invoice_pdf(self):
        self.pdf.open("b")
        try:
            return self.pdf.name, self.pdf.read()
        finally:
            self.pdf.close()

    def finalize_invoice(self):
        """Generate PDF and mark invoice as unpaid."""
        self._generate_invoice_pdf()
        self.state = self.UNPAID
        self.save()

    def _generate_invoice_pdf(self):
        """Generate PDF data by calling billable.me."""
        params = self.STATIC_BILLABLEME_PARAMS.copy()
        params.update({
            'invoice_number': str(self.pk),
            'invoice_date': self.timestamp.date().isoformat(),
            'company_name': self.company_name,
            'company_info': self.company_info,
            'recipient_info': self.recipient_info,
            'tax_name': self.tax_name,
            'tax_percentage': '',
            'currency_symbol': self.currency_symbol,
            'notes_a': self.payment_details % {
                'reference': self.reference,
            },
            'notes_b': self.additional_notes,
        })

        for i, item in enumerate(self.items):
            params['items.%d.description'] = item.description
            params['items.%d.quantity'] = str(item.quantity)
            params['items.%d.price'] = str(item.price)

        subtotal = sum([i.price for i in self.items])
        params['subtotal'] = "%.2f" % subtotal

        if self.tax_percentage:
            tax_amount = "%.2f" % (subtotal * self.tax_percentage)
            total = subtotal + tax_amount
        else:
            tax_amount = "N/A"
            total = subtotal

        params['tax_amount'] = tax_amount
        params['total'] = "%.2f" % total

        response = requests.post(settings.WAFER_BILLABLE_ME, data=params)
        pdf_data = response.content

        self.pdf.save(self.invoice_pdf_filename(),
                      ContentFile(pdf_data))


class InvoiceItem(models.Model):
    description = models.CharField(max_length=255, required=True)
    quantity = models.IntegerField(require=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    invoice = models.ForeignKey(Invoice)
