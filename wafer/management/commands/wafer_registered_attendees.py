import codecs
import sys

from django.conf import settings
from django.core.management.base import BaseCommand

from wafer.users.models import UserProfile

if sys.version_info >= (3,):
    import csv
else:
    from backports import csv


class RegisteredUserList(object):
    def fields(self):
        return ('username', 'name', 'email')

    def details(self, person):
        user = person.user
        return (
            user.username,
            person.display_name(),
            user.email,
        )

    def attendees(self):
        people = UserProfile.objects.all().order_by(
            'user__username').prefetch_related('user', 'kv')

        for person in people:
            if person.is_registered():
                yield self.details(person)


class TicketRegisteredUserList(RegisteredUserList):
    def fields(self):
        return super(TicketRegisteredUserList, self).fields() + (
            'ticket_type', 'ticket_barcode')

    def details(self, person):
        ticket = person.user.ticket.first()
        details = (None, None)
        if ticket:
            details = (ticket.type.name, ticket.barcode)
        return super(TicketRegisteredUserList, self).details(person) + details


class Command(BaseCommand):
    help = "Dump attendee registration information"

    def handle(self, *args, **options):
        stream_writer = codecs.getwriter('utf-8')
        bytestream = getattr(sys.stdout, 'buffer', sys.stdout)
        csv_file = csv.writer(stream_writer(bytestream))

        if settings.WAFER_REGISTRATION_MODE == 'ticket':
            user_list = TicketRegisteredUserList()
        else:
            user_list = RegisteredUserList()

        csv_file.writerow(user_list.fields())
        for row in user_list.attendees():
            csv_file.writerow(row)
