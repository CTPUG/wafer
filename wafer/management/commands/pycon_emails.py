import sys
import csv
from optparse import make_option

from django.core.management.base import BaseCommand

from wafer.models import AttendeeRegistration

from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "List speaker or attendee email addresses."

    option_list = BaseCommand.option_list + tuple([
        make_option('--speakers', action="store_true", default=False,
                    help='List speaker email addresses only'),
        make_option('--unpaid', action="store_true", default=False,
                    help='Only list people who have not paid.'),
        make_option('--paid', action="store_true", default=False,
                    help='Only list people who have paid.'),
        make_option('--registered', action="store_true", default=False,
                    help='Only list people not on the waiting list.'),
        make_option('--waiting', action="store_true", default=False,
                    help='Only list people on the waiting list.'),
        make_option('--active', action="store_true", default=False,
                    help='Only list people who are active.'),
        make_option('--inactive', action="store_true", default=False,
                    help='Only list people who are inactive.'),
    ])

    def _attendee_emails(self, options):
        query = {}
        if options['unpaid']:
            query['invoice_paid'] = False
        if options['paid']:
            query['invoice_paid'] = True
        if options['registered']:
            query['on_waiting_list'] = False
        if options['waiting']:
            query['on_waiting_list'] = True
        if options['active']:
            query['active'] = True
        if options['inactive']:
            query['active'] = False

        people = AttendeeRegistration.objects.filter(**query)

        csv_file = csv.writer(sys.stdout)
        for person in people:
            row = [x.encode("utf-8")
                   for x in (person.fullname(), person.email)]
            csv_file.writerow(row)

    def _speaker_emails(self, options):
        # Should grow more options - accepted talks, under consideration, etc.
        people = User.objects.filter(contact_talks__isnull=False).all()

        csv_file = csv.writer(sys.stdout)
        for person in people:
            titles = [x.titles for x in person.contact_talks.all()]
            row = [x.encode("utf-8")
                   for x in (person.get_full_name(), person.email,
                             ' '.join(titles))]
            csv_file.writerow(row)

    def handle(self, *args, **options):

        if options['speakers']:
            self._speaker_emails(options)
        else:
            self._attendee_emails(options)
