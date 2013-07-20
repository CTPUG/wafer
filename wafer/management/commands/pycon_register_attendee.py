from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import models


class Command(BaseCommand):
    help = "Manually register an attendee."

    def handle(self, *args, **options):
        # FIXME: Redo
        print 'Unimplemented'
