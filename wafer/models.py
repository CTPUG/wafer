'''
Created on 29 Jun 2012

@author: euan
'''
from django.db import models
from django.conf import settings
from django.core.mail import EmailMessage

from wafer import constants

WAITING_LIST_ON = getattr(settings, 'WAITING_LIST_ON', False)


class AttendeeRegistration(models.Model):

    name = models.CharField(max_length=128)
    surname = models.CharField(max_length=128, null=True)
    email = models.EmailField()
    contact_number = models.CharField(max_length=16, null=True, blank=True)
    registration_type = models.IntegerField(
        choices=constants.REGISTRATION_TYPES, null=True)
    comments = models.TextField(null=True, blank=True)

    # TODO: many-to-many field to link to invoices

    timestamp = models.DateTimeField(auto_now_add=True)
    on_waiting_list = models.BooleanField(default=WAITING_LIST_ON)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return u'%s %s (%s)' % (self.name, self.surname, self.email)

    def fullname(self):
        return u"%s %s" % (self.name.strip(), self.surname.strip())

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


def post_registration_save(sender, instance, created, **kwargs):
    if created:
        instance.send_registration_email()


models.signals.post_save.connect(post_registration_save,
                                 sender=AttendeeRegistration)
