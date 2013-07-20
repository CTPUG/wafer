from optparse import make_option

from django.core.management.base import BaseCommand
from wafer.conf_registration.models import RegisteredAttendee


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
        # FIXME: Reimplement
        print 'Unimplemented - to be redone when registration is finished'
