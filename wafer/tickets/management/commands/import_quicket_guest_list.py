import csv
import logging

from django.core.management.base import BaseCommand, CommandError

from wafer.tickets.views import import_ticket


class Command(BaseCommand):
    args = '<csv file>'
    help = "Import a guest list CSV from Quicket"

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('1 CSV File required')

        logging.basicConfig(level=logging.INFO)

        columns = ('Ticket Number', 'Ticket Barcode', 'Purchase Date',
                   'Ticket Type', 'Ticket Holder', 'Email', 'Cellphone',
                   'Checked in', 'Checked in date', 'Checked in by',
                   'Complimentary')
        keys = [column.lower().replace(' ', '_') for column in columns]

        with open(args[0], 'r') as f:
            reader = csv.reader(f)

            header = tuple(next(reader))
            if header != columns:
                raise CommandError('CSV format has changed. Update wafer')

            for row in reader:
                ticket = dict(zip(keys, row))
                import_ticket(ticket['ticket_barcode'],
                              ticket['ticket_type'],
                              ticket['email'])
