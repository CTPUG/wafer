from optparse import make_option

from django.core.management.base import BaseCommand

from wafer.models import AttendeeRegistration


class Command(BaseCommand):
    help = "Move an attendee between states."

    option_list = BaseCommand.option_list + tuple([
        make_option('--email-address', help='Email address for attendee'),
        make_option('--pk', help='Private key of attendee'),
        make_option('--off-waiting-list', action='store_true', default=False,
                    help='Also move the attendee off the waiting list.'),
    ])

    def handle(self, *args, **options):
        email = options.get('email_address')
        pk = options.get('pk')
        off_waiting_list = options.get('off_waiting_list')

        qparams = {}
        if email:
            qparams['email'] = email
        if pk:
            qparams['pk'] = pk
        attendee = AttendeeRegistration.objects.get(**qparams)

        if off_waiting_list:
            if not attendee.on_waiting_list:
                print "Attendee not on waiting list! Aborting."
                return
            attendee.on_waiting_list = False

        attendee.save()

        if attendee.invoice_pdf is None:
            attendee.generate_invoice_pdf()

        attendee.send_registration_email(generate_invoice=False)

        print "Sent invoice for attendee %r" % (attendee,)
        print "  Name: %s %s" % (attendee.name, attendee.surname)
        print "  E-mail: %s" % (attendee.email,)
        print "  Contact number: %s" % (attendee.contact_number,)
        print "  Registration type: %s" % (attendee.registration_type,)
        print "  Comments: %s" % (attendee.comments,)
        print "  Invoice paid: %s" % (attendee.invoice_paid,)
        print "  Invoice #: %s" % (attendee.pk,)
        print "  Invoide ID: %s" % (attendee.invoice_id,)
