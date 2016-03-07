import codecs
import csv
import sys

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string

from wafer.users.models import UserProfile


class Command(BaseCommand):
    help = "Dump attendee registration information"

    def _get_fields(self):
        form_class = import_string(settings.WAFER_REGISTRATION_FORM)
        form = form_class()
        return form.fields.keys()

    def _iter_people(self):
        people = UserProfile.objects.all().order_by(
            'user__username').prefetch_related('user', 'kv')

        for person in people:
            if person.kv.exists():
                yield person

    def _iter_registration(self, person, group, fields):
        registration_data = person.kv.filter(group=group)
        for field in fields:
            item = registration_data.filter(key=field).first()
            if item:
                yield item.value
            else:
                yield None

    def _user_details(self, person):
        user = person.user
        yield user.username
        yield person.display_name()
        yield user.email

    def handle(self, *args, **options):
        stream_writer = codecs.getwriter('utf-8')
        csv_file = csv.writer(stream_writer(sys.stdout))

        fields = self._get_fields()
        csv_file.writerow(['username', 'name', 'email'] + fields)

        group = Group.objects.get_by_natural_key(
            settings.WAFER_REGISTRATION_GROUP)

        for person in self._iter_people():
            row = list(self._user_details(person))
            row += list(self._iter_registration(person, group, fields))
            csv_file.writerow(row)
