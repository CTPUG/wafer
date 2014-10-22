from django.core.management.base import BaseCommand

from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Misc stats."

    option_list = BaseCommand.option_list + tuple([
    ])

    def _speakers(self, *args, **kwargs):
        return get_user_model().objects.filter(
            contact_talks__isnull=False).filter(*args, **kwargs).count()

    def handle(self, *args, **options):
        print("Speakers:\n")

        # FIXME: more stats - accepted, rejected, pending, etc.
        print("  Total: %s" % self._speakers())
