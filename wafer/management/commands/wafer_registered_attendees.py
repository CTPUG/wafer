import codecs
import sys

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string

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


class FormRegisteredUserList(RegisteredUserList):
    def __init__(self):
        self.group = Group.objects.get_by_natural_key('Registration')
        form_class = import_string(settings.WAFER_REGISTRATION_FORM)
        self.form = form_class()

    def fields(self):
        return super(FormRegisteredUserList, self).fields() + tuple(
            self.form.fields.keys())

    def _iter_details(self, registration_data):
        for field in self.form.fields.keys():
            item = registration_data.filter(key=field).first()
            if item:
                yield item.value
            else:
                yield None

    def details(self, person):
        registration_data = person.kv.filter(group=self.group)
        details = tuple(self._iter_details(registration_data))
        return super(FormRegisteredUserList, self).details(person) + details


class Command(BaseCommand):
    help = "Dump attendee registration information"

    def handle(self, *args, **options):
        stream_writer = codecs.getwriter('utf-8')
        bytestream = getattr(sys.stdout, 'buffer', sys.stdout)
        csv_file = csv.writer(stream_writer(bytestream))

        if settings.WAFER_REGISTRATION_MODE == 'ticket':
            user_list = TicketRegisteredUserList()
        elif settings.WAFER_REGISTRATION_MODE == 'form':
            user_list = FormRegisteredUserList()
        else:
            raise NotImplemented('Unknown WAFER_REGISTRATION_MODE')

        csv_file.writerow(user_list.fields())
        for row in user_list.attendees():
            csv_file.writerow(row)
