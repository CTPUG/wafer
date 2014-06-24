import csv

from django.core.management.base import BaseCommand, CommandError

from wafer.tickets.views import import_ticket


class Command(BaseCommand):
    args = '<csv file>'
    help = "Import a guest list CSV from Quicket"

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('1 CSV File required')

        with open(args[0], 'r') as f:
            reader = csv.reader(f)

            header = next(reader)
            if len(header) != 11:
                raise CommandError('CSV format has changed. Update wafer')

            for ticket in reader:
                self.import_ticket(*ticket)

    def import_ticket(self, ticket_number, ticket_barcode, purchase_date,
                      ticket_type, ticket_holder, email, cellphone, checked_in,
                      checked_in_date, checked_in_by, complimentary):
        import_ticket(ticket_barcode, ticket_type, email)
