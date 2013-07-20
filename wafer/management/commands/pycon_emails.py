import sys
import csv
from optparse import make_option

from django.core.management.base import BaseCommand

from django.contrib.auth.models import User
from wafer.conf_registration.models import RegisteredAttendee


class Command(BaseCommand):
    help = "List speaker or attendee email addresses."

    option_list = BaseCommand.option_list + tuple([
        make_option('--speakers', action="store_true", default=False,
                    help='List speaker email addresses only'),
        make_option('--waiting', action="store_true", default=False,
                    help='Only list people on the waiting list.'),
    ])

    def _attendee_emails(self, options):
        query = {}
        if options['waiting']:
            query['waitlist'] = True

        people = RegisteredAttendee.objects.filter(**query)

        csv_file = csv.writer(sys.stdout)
        for person in people:
            row = [x.encode("utf-8")
                   for x in (person.name, person.email)]
            csv_file.writerow(row)

    def _speaker_emails(self, options):
        # Should grow more options - accepted talks, under consideration, etc.
        people = User.objects.filter(contact_talks__isnull=False).all()

        csv_file = csv.writer(sys.stdout)
        for person in people:
            titles = [x.title for x in person.contact_talks.all()]
            # XXX: Should we check for username here, since full name
            # may be blank
            row = [x.encode("utf-8")
                   for x in (person.get_full_name(), person.email,
                             ' '.join(titles))]
            csv_file.writerow(row)

    def handle(self, *args, **options):

        if options['speakers']:
            self._speaker_emails(options)
        else:
            self._attendee_emails(options)
