import sys
import csv
from optparse import make_option

from django.core.management.base import BaseCommand

from django.contrib.auth import get_user_model
from wafer.talks.models import ACCEPTED


class Command(BaseCommand):
    help = ("List speakers and associated tickets. By default, only lists"
            " speakers for accepted talk, but this can be overriden by"
            " the --all option")

    option_list = BaseCommand.option_list + tuple([
        make_option('--all', action="store_true", default=False,
                    help='List speakers and tickets (for all talks)'),
    ])

    def _speaker_tickets(self, options):
        people = get_user_model().objects.filter(
            talks__isnull=False).distinct()

        csv_file = csv.writer(sys.stdout)
        for person in people:
            # We query talks to filter out the speakers from ordinary
            # accounts
            if options['all']:
                titles = [x.title for x in person.talks.all()]
            else:
                titles = [x.title for x in
                          person.talks.filter(status=ACCEPTED)]
            if not titles:
                continue
            tickets = person.ticket.all()
            if tickets:
                ticket = u'%d' % tickets[0].barcode
            else:
                ticket = u'NO TICKET PURCHASED'
            row = [x.encode("utf-8") for x in (person.get_full_name(),
                   person.email,
                   ticket)]
            csv_file.writerow(row)

    def handle(self, *args, **options):
        self._speaker_tickets(options)
