import os
import sys
import csv
import subprocess
import re

from django.core.management.base import BaseCommand

from pycon.models import AttendeeRegistration


class Command(BaseCommand):
    help = "Summarize attendee invoices."

    def handle(self, *args, **options):
        parser = InvoiceParser()
        people = AttendeeRegistration.objects.filter(
                on_waiting_list=False, active=True)

        csv_file = csv.writer(sys.stdout)
        csv_file.writerow(["name", "email", "invoice no.", "reference",
                           "shared invoice", "amount", "paid"])
        for person in people:
            if not person.invoice_pdf.name:
                invoice = Invoice('??', '??')
            else:
                invoice = parser.parse(person.invoice_pdf.path)
            row = [person.fullname(), person.email,
                   person.pk, person.payment_reference(),
                   invoice.shared, invoice.amount,
                   person.invoice_paid]
            row = [unicode(x).encode("utf-8") for x in row]
            csv_file.writerow(row)


class Invoice(object):
    def __init__(self, amount, shared):
        self.amount = amount
        self.shared = shared


class InvoiceParser(object):

    INVOICE_RE = re.compile(r"""
    .*?
    ^T(\ )*otal$
    .*?
    ^(?P<amount>[0-9]+\.[0-9]{2})$
    .*
    """, re.MULTILINE | re.DOTALL | re.VERBOSE)

    def parse(self, filename):
        text = subprocess.check_output(["pdftotext", filename, "-"])
        match = self.INVOICE_RE.match(text)
        amount = match.group('amount') if match else '??'
        shared = os.path.islink(filename)
        return Invoice(amount, shared)
