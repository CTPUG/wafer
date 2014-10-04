from django.core.management.base import BaseCommand

from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Misc stats."

    option_list = BaseCommand.option_list + tuple([
    ])

    def _speakers(self, *args, **kwargs):
        return User.objects.filter(contact_talks__isnull=False).filter(
            *args, **kwargs).count()

    def handle(self, *args, **options):
        print "Speakers:"
        print

        # FIXME: more stats - accepted, rejected, pending, etc.
        print "  Total:", self._speakers()
