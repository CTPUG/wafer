from django.core.management.base import BaseCommand

from django.contrib.auth.models import User
from wafer.conf_registration.models import RegisteredAttendee


class Command(BaseCommand):
    help = "Misc stats."

    option_list = BaseCommand.option_list + tuple([
    ])

    def _attendees(self, *args, **kwargs):
        return RegisteredAttendee.objects.filter(*args, **kwargs).count()

    def _speakers(self, *args, **kwargs):
        return User.objects.filter(contact_talks__isnull=False).filter(
            *args, **kwargs).count()

    def handle(self, *args, **options):
        print "Attendees:", self._attendees()
        print

        # FIXME: more stats (registered, etc.)

        print "  Waiting:", self._attendees(waitlist=True)

        print "Speakers:"
        print

        # FIXME: more stats - accepted, rejected, pending, etc.
        print "  Total:", self._speakers()
