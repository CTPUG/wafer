from django.core.management.base import BaseCommand

from wafer.models import AttendeeRegistration
from wafer.constants import (REGISTRATION_TYPE_CORPORATE,
                             REGISTRATION_TYPE_INDIVIDUAL,
                             REGISTRATION_TYPE_STUDENT)

from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Manually register an attendee."

    option_list = BaseCommand.option_list + tuple([
    ])

    def _attendees(self, *args, **kwargs):
        return AttendeeRegistration.objects.filter(*args, **kwargs).count()

    def _speakers(self, *args, **kwargs):
        return User.objects.filter(contact_talks__isnull=False).filter(
            *args, **kwargs).count()

    def handle(self, *args, **options):
        print "Attendees:", self._attendees()
        print

        TYPES = [("Corporate", REGISTRATION_TYPE_CORPORATE),
                 ("Individual", REGISTRATION_TYPE_INDIVIDUAL),
                 ("Student", REGISTRATION_TYPE_STUDENT),
                 ]

        print "  Registered:", self._attendees(on_waiting_list=False,
                                               active=True)
        for label, rtype in TYPES:
            paid = self._attendees(on_waiting_list=False, active=True,
                                   registration_type=rtype, invoice_paid=True)
            unpaid = self._attendees(on_waiting_list=False, active=True,
                                     registration_type=rtype,
                                     invoice_paid=False)
            print "    %s: %d (unpaid: %d)" % (label, paid + unpaid, unpaid)

        print

        print "  Waiting:", self._attendees(on_waiting_list=True, active=True)
        for label, rtype in TYPES:
            print "    %s:" % label, self._attendees(on_waiting_list=True,
                                                     active=True,
                                                     registration_type=rtype)

        print

        print "  Inactive:", self._attendees(active=False)
        print

        print "Speakers:"
        print

        # FIXME: more stats - accepted, rejected, pending, etc.
        print "  Total:", self._speakers()
