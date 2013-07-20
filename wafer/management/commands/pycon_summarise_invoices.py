from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Summarize attendee invoices."

    def handle(self, *args, **options):
        # FIXME: Redo
        print 'Unimplemented.'
