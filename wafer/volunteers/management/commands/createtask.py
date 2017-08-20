from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError

from wafer.volunteers.models import Task


class Command(BaseCommand):
    help = 'Creates a task'

    def add_arguments(self, parser):
        parser.add_argument('name')
        parser.add_argument('description')
        parser.add_argument('date')
        parser.add_argument('start_time')
        parser.add_argument('end_time')
        parser.add_argument('nbr_volunteers_min', type=int,
                            nargs='?', default=1)
        parser.add_argument('nbr_volunteers_max', type=int,
                            nargs='?', default=1)

    def handle(self, *args, **options):
        try:
            task = Task.objects.create(
                name=options['name'],
                description=options['description'],
                date=options['date'],
                start_time=options['start_time'],
                end_time=options['end_time'],
                nbr_volunteers_min=options['nbr_volunteers_min'],
                nbr_volunteers_max=options['nbr_volunteers_max'])
        except ValidationError as e:
            raise CommandError('Invalid task: "%s"' % e)

        task.save()

        self.stdout.write('Successfully created task: "%s"' % task)
