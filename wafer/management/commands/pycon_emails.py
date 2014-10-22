import sys
import csv
from optparse import make_option

from django.core.management.base import BaseCommand

from django.contrib.auth import get_user_model
from wafer.talks.models import ACCEPTED


class Command(BaseCommand):
    help = "List author or web-site user email addresses."

    option_list = BaseCommand.option_list + tuple([
        make_option('--authors', action="store_true", default=False,
                    help='List author email addresses only'
                    ' (for accepted talks)'),
        make_option('--allauthors', action="store_true", default=False,
                    help='List author emails only (for all talks)'),
        make_option('--speakers', action="store_true", default=False,
                    help='List speaker email addresses'
                    ' (for accepted talks)'),
        make_option('--allspeakers', action="store_true", default=False,
                    help='List speaker email addresses'
                    ' (for all talks)'),
    ])

    def _website_user_emails(self, options):
        query = {}

        people = get_user_model().objects.all()

        csv_file = csv.writer(sys.stdout)
        for person in people:
            row = [x.encode("utf-8")
                   for x in (person.username, person.get_full_name(), person.email)]
            csv_file.writerow(row)

    def _author_emails(self, options):
        # Should grow more options - accepted talks, under consideration, etc.
        people = get_user_model().objects.filter(
            contact_talks__isnull=False).distinct()

        csv_file = csv.writer(sys.stdout)
        for person in people:
            if options['allauthors']:
                titles = [x.title for x in person.contact_talks.all()]
            else:
                titles = [x.title for x in
                          person.contact_talks.filter(status=ACCEPTED)]
                if not titles:
                    continue
            # get_full_name may be blank, since we don't require that
            # the user specify it, but we will have the email as an
            # identifier
            row = [x.encode("utf-8")
                   for x in (person.get_full_name(), person.email,
                             ';'.join(titles))]
            csv_file.writerow(row)

    def _speaker_emails(self, options):
        people = get_user_model().objects.filter(talks__isnull=False).distinct()

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
                             ';'.join(titles))]
            csv_file.writerow(row)

    def handle(self, *args, **options):

        if options['authors'] or options['allauthors']:
            self._author_emails(options)
        elif options['speakers'] or options['allspeakers']:
            self._speaker_emails(options)
        else:
            self._website_user_emails(options)
