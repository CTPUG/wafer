'''
Created on 29 Jun 2012

@author: euan
'''
from uuid import uuid4
import urllib2
import urllib
import re
import unicodedata
import json

from django.db import models
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.core.urlresolvers import reverse
from django.contrib.sites.models import get_current_site
from django.core.files.base import ContentFile

from pycon import constants

WAITING_LIST_ON = getattr(settings, 'WAITING_LIST_ON', False)


def normalize_unicode(u):
    return unicodedata.normalize('NFKD', u).encode('ascii', 'ignore')


class AttendeeRegistration(models.Model):

    name = models.CharField(max_length=128)
    surname = models.CharField(max_length=128, null=True)
    email = models.EmailField()
    contact_number = models.CharField(max_length=16, null=True, blank=True)
    registration_type = models.IntegerField(
        choices=constants.REGISTRATION_TYPES, null=True)
    comments = models.TextField(null=True, blank=True)
    invoice_id = models.CharField(max_length=32, editable=False,
                                  default=lambda: uuid4().hex)
    invoice_paid = models.BooleanField(default=False)
    invoice_pdf = models.FileField(upload_to='invoices', null=True,
                                   editable=False)
    # invoice_billable_params is JSON encoded
    invoice_billable_params = models.TextField(null=True, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    on_waiting_list = models.BooleanField(default=WAITING_LIST_ON)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return u'%s %s (%s)' % (self.name, self.surname, self.email)

    def fullname(self):
        return u"%s %s" % (self.name.strip(), self.surname.strip())

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

        data = urllib.urlencode(params)
        pdf_data = urllib2.urlopen(billable_me_url, data=data).read()

        self.invoice_billable_params = json.dumps(params)
        self.invoice_pdf.save(self.invoice_pdf_filename(),
                              ContentFile(pdf_data))

    def send_registration_email(self, generate_invoice=True):
        if self.on_waiting_list:
            self.send_waiting_list_email()
        else:
            self.send_invoice_email(generate_invoice=True)

    def send_waiting_list_email(self):
        fullname = u"%s %s" % (self.name, self.surname)
        subject = 'PyCon ZA 2012 Waiting List - %s' % fullname
        params = {
            'fullname': fullname,
        }
        text = (
            "Thank you for expressing interest in PyCon ZA 2012.\n"
            "\n"
            "PyCon ZA 2012 is currently full. You've been added to the "
            "waiting list. We'll contact you as soon as space opens up!\n"
            "\n"
            "If you have any questions, please contact "
            "Wendy Griffiths on +27 82 377 5913 or e-mail team@za.pycon.org.\n"
            "\n"
            "Holding thumbs that we'll get to see you in October!\n"
            "\n"
        ) % params
        waiting_text = (
            "%(fullname)s has been added to the waiting list for PyConZA "
            "2012.\n"
            "\n"
        ) % params

        mail = EmailMessage(subject, text, settings.DEFAULT_FROM_EMAIL,
                            [self.email])
        mail.send(fail_silently=True)
        waiting_mail = EmailMessage(subject, waiting_text,
                                    settings.DEFAULT_FROM_EMAIL,
                                    settings.FINANCIAL_ADMINS)
        waiting_mail.send(fail_silently=True)

    def send_invoice_email(self, generate_invoice=True):
        fullname = u"%s %s" % (self.name, self.surname)
        subject = 'PyCon ZA 2012 Invoice - %s' % fullname
        params = {
            'invoice_url': self.invoice_url(),
            'fullname': fullname,
            'reference': self.payment_reference(),
        }
        text = (
            "Thank you for registering for PyCon ZA 2012.\n"
            "\n"
            "Your invoice is attached. A copy can be downloaded from:\n"
            "\n"
            "  %(invoice_url)s\n"
            "\n"
            "You can pay by EFT to the bank account below:\n"
            "\n"
            "  Account number: 9275706696\n"
            "  Branch code: 632005\n"
            "  Account name: PyCon Conference\n"
            "  Bank: ABSA\n"
            "  Reference: %(reference)s\n"
            "\n"
            "For assistance with registration and payment please contact "
            "Wendy Griffiths on +27 82 377 5913 or e-mail team@za.pycon.org.\n"
            "\n"
            "If you need to pay by credit card, you may pay at "
            "http://www.quicket.co.za/events/933-pyconza-2012. Please fill in "
            "the same details you used when registering on the PyConZA site.\n"
            "\n"
            "Looking forward to seeing you in October!\n"
            "\n"
        ) % params
        financial_text = (
            "%(fullname)s has registered for PyConZA 2012.\n"
            "\n"
            "Their invoice is at:\n"
            "\n"
            "  %(invoice_url)s\n"
            "\n"
            "Expected reference: %(reference)s\n"
            "\n"
        ) % params

        if generate_invoice:
            self.generate_invoice_pdf()
        pdf_filename, pdf_data = self.get_invoice_pdf()

        mail = EmailMessage(subject, text, settings.DEFAULT_FROM_EMAIL,
                            [self.email])
        mail.attach(pdf_filename, pdf_data, 'application/pdf')
        mail.send(fail_silently=True)
        fin_mail = EmailMessage(subject, financial_text,
                                settings.DEFAULT_FROM_EMAIL,
                                settings.FINANCIAL_ADMINS)
        fin_mail.attach(pdf_filename, pdf_data, 'application/pdf')
        fin_mail.send(fail_silently=True)


class SpeakerRegistration(models.Model):

    name = models.CharField(max_length=128)
    surname = models.CharField(max_length=128, null=True)
    email = models.EmailField()
    contact_number = models.CharField(max_length=16, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    bio = models.TextField(null=True)
    photo = models.ImageField(upload_to='speaker-photos', null=True,
                              blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    talk_title = models.CharField(max_length=128, null=True)
    talk_type = models.IntegerField(choices=constants.TALK_TYPES, null=True)
    talk_level = models.IntegerField(choices=constants.TALK_LEVELS, null=True)
    talk_category = models.CharField(max_length=64, null=True)
    talk_duration = models.CharField(max_length=32, null=True)
    talk_description = models.TextField(null=True)
    talk_abstract = models.TextField(null=True)
    talk_notes = models.TextField(null=True)

    approved = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s %s (%s)' % (self.name, self.surname, self.email)

    def fullname(self):
        return u"%s %s" % (self.name.strip(), self.surname.strip())

    def send_registration_email(self):
        text = (
            "Thanks for showing your interest. "
            "We'll get in touch shortly."
        )
        send_mail('PyCon ZA 2012', text, settings.DEFAULT_FROM_EMAIL,
                  [self.email], fail_silently=True)


def post_registration_save(sender, instance, created, **kwargs):
    if created:
        instance.send_registration_email()


models.signals.post_save.connect(post_registration_save,
                                 sender=AttendeeRegistration)

models.signals.post_save.connect(post_registration_save,
                                 sender=SpeakerRegistration)
