from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import models

from wafer.models import AttendeeRegistration, post_registration_save
from wafer import constants


class Command(BaseCommand):
    help = "Manually register an attendee."

    RTYPES = {
        'corporate': constants.REGISTRATION_TYPE_CORPORATE,
        'individual': constants.REGISTRATION_TYPE_INDIVIDUAL,
        'student': constants.REGISTRATION_TYPE_STUDENT,
    }

    option_list = BaseCommand.option_list + tuple([
        make_option('--fullname', help='Full name for attendee'),
        make_option('--email-address', help='Email address for attendee'),
        make_option('--contact-number', help='Contact number for attendee'),
        make_option('--type', choices=sorted(RTYPES.keys()),
                    help='Type of registration'),
        make_option('--comments', help='Additional comments'),
        make_option('--paid', action='store_true', default=False,
                    help='Mark attendee as paid'),
        make_option('--send-invoice-email', action='store_true',
                    default=False,
                    help='Send an invoice email to the user'),
        make_option('--reg-kind', help='Override the regisration'
                    ' description. Default depends on --type.',
                    default=None),
        make_option('--reg-price', type='int', help='Override the'
                    ' registration price. Default depends on --type.',
                    default=None),
    ])

    def handle(self, *args, **options):
        # disconnect email sending
        models.signals.post_save.disconnect(post_registration_save,
                                            sender=AttendeeRegistration)

        fullname = options.get('fullname')
        email = options.get('email_address')
        contact_number = options.get('contact_number')
        rtype = options.get('type')
        comments = options.get('comments')
        invoice_paid = options.get('paid')
        reg_kind = options.get('reg_kind')
        reg_price = options.get('reg_price')

        name, _sep, surname = (fullname or '').partition(' ')
        registration_type = self.RTYPES.get(rtype)

        if not all([name, surname, email, registration_type is not None]):
            print ("Please supply a name, surname, email address and"
                   " registration type.")
            return

        attendee = AttendeeRegistration(name=name, surname=surname,
                                        email=email,
                                        contact_number=contact_number,
                                        registration_type=registration_type,
                                        comments=comments,
                                        invoice_paid=invoice_paid)
        attendee.save()
        attendee.generate_invoice_pdf(reg_kind=reg_kind, reg_price=reg_price)
        if options.get('send_invoice_email'):
            attendee.send_registration_email(generate_invoice=False)

        print "Created attendee %r" % (attendee,)
        print "  Name: %s %s" % (attendee.name, attendee.surname)
        print "  E-mail: %s" % (attendee.email,)
        print "  Contact number: %s" % (attendee.contact_number,)
        print "  Registration type: %s" % (attendee.registration_type,)
        print "  Comments: %s" % (attendee.comments,)
        print "  Invoice paid: %s" % (attendee.invoice_paid,)
        print "  Invoice #: %s" % (attendee.pk,)
        print "  Invoide ID: %s" % (attendee.invoice_id,)
