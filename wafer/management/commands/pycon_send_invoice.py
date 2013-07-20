from optparse import make_option

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Move an attendee between states."

    def handle(self, *args, **options):
        # FIXME: redo
        print 'Unimplemented'
