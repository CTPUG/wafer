import sys
import csv

from django.core.management.base import BaseCommand

from django.contrib.auth import get_user_model
from wafer.talks.models import ACCEPTED


class Command(BaseCommand):
    help = "List contact details for the speakers."

    def add_arguments(self, parser):
        parser.add_argument('--speakers', action="store_true",
                            help='List speaker email addresses'
                                 ' (for accepted talks)')
        parser.add_argument('--allspeakers', action="store_true",
                            help='List speaker email addresses'
                                 ' (for all talks)')

    def _speaker_emails(self, options):
        people = get_user_model().objects.filter(
            talks__isnull=False).distinct()

        csv_file = csv.writer(sys.stdout)
        for person in people:
            if options['allspeakers']:
                titles = [x.title for x in person.talks.all()]
            else:
                titles = [x.title for x in
                          person.talks.filter(status=ACCEPTED)]
                if not titles:
                    continue
            row = [x
                   for x in (person.userprofile.display_name(), person.email,
                   person.userprofile.contact_number or 'NO CONTACT INFO',
                   ';'.join(titles))]
            csv_file.writerow(row)

    def handle(self, *args, **options):
        self._speaker_emails(options)
