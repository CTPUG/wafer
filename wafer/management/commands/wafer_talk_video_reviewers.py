import sys
import csv

from django.core.management.base import BaseCommand

from wafer.talks.models import Talk, ACCEPTED


class Command(BaseCommand):
    help = ("List talks and the associated video_reviewer emails."
            " Only reviewers for accepted talks are listed")

    def _video_reviewers(self, options):
        talks = Talk.objects.filter(status=ACCEPTED)

        csv_file = csv.writer(sys.stdout)
        for talk in talks:
            reviewer = talk.video_reviewer
            if not reviewer:
                reviewer = 'NO REVIEWER'
            row = [talk.title,
                   talk.get_authors_display_name(),
                   reviewer,
                  ]
            csv_file.writerow(row)

    def handle(self, *args, **options):
        self._video_reviewers(options)
