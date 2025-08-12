import csv
import logging

from django.core.management.base import BaseCommand, CommandError

from wafer.tickets.views import import_ticket


class Command(BaseCommand):

    def add_arguments(self, parser):
        """Add a required file input"""
        parser.add_argument('csv_file', help="Import a guest list CSV from Quicket")

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        logging.basicConfig(level=logging.INFO)

        required_keys = ['ticket_barcode', 'ticket_type', 'email']

        with open(csv_file, 'r') as f:
            reader = csv.reader(f)

            header = tuple(next(reader))
            keys = [column.lower().replace(' ', '_') for column in header]
            for expected_key in required_keys:
                if expected_key not in keys:
                    raise CommandError('CSV format has changed. Update wafer')

            for row in reader:
                ticket = dict(zip(keys, row))
                import_ticket(ticket['ticket_barcode'],
                              ticket['ticket_type'],
                              ticket['email'])
