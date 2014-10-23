import sys
import csv
from optparse import make_option

from django.core.management.base import BaseCommand

from django.contrib.auth import get_user_model
from wafer.talks.models import ACCEPTED


class Command(BaseCommand):
    help = "List contact details for the speakers."

    option_list = BaseCommand.option_list + tuple([
        make_option('--speakers', action="store_true", default=False,
                    help='List speaker email addresses'
                    ' (for accepted talks)'),
        make_option('--allspeakers', action="store_true", default=False,
                    help='List speaker email addresses'
                    ' (for all talks)'),
    ])

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
            # get_full_name may be blank, since we don't require that
            # the user specify it, but we will have the email as an
            # identifier
            row = [x.encode("utf-8")
                   for x in (person.get_full_name(), person.email,
                   person.userprofile.contact_number or 'NO CONTACT INFO',
                   ';'.join(titles))]
            csv_file.writerow(row)

    def handle(self, *args, **options):
        self._speaker_emails(options)
