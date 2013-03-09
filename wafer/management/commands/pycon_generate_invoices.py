from optparse import make_option

from django.core.management.base import BaseCommand

from pycon.models import AttendeeRegistration


class Command(BaseCommand):
    help = "Generating missing PyCon attendee invoices."

    option_list = BaseCommand.option_list + tuple([
        make_option('--email-address', help='Generate an attendee invoice for'
                    ' just the given email address.'),
        make_option('--overwrite', action="store_true", default=False,
                    help='Overwrite any existing invoices.'),
    ])

    def handle(self, *args, **options):
        email = options.get('email_address')
        overwrite = options.get('overwrite')
        if email is not None:
            attendee = AttendeeRegistration.objects.get(email=email)
            attendees = [attendee]
        else:
            attendees = AttendeeRegistration.objects.all()

        for attendee in attendees:
            who = "%s %s (%s)" % (attendee.name, attendee.surname,
                                  attendee.email)
            if attendee.invoice_pdf.name is None or overwrite:
                print "Generated invoice for %s." % (who,)
                attendee.generate_invoice_pdf()
            else:
                print "Skipping existing invoice for %s." % (who,)
                continue
