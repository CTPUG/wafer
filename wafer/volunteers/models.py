from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import date

from wafer.schedule.models import Venue
from wafer.talks.models import Talk


@python_2_unicode_compatible
class Volunteer(models.Model):

    RATINGS = (
            (0, 'No longer welcome'),
            (1, 'Poor'),
            (2, 'Not great'),
            (3, 'Average'),
            (4, 'Good'),
            (5, 'Superb'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                related_name='volunteer')

    tasks = models.ManyToManyField('Task', blank=True)
    preferred_categories = models.ManyToManyField('TaskCategory', blank=True)

    staff_rating = models.IntegerField(null=True, blank=True, choices=RATINGS)
    staff_notes = models.TextField(null=True, blank=True)

    @property
    def annotated_tasks(self):
        return self.tasks.annotate_all()

    def __str__(self):
        return u'%s' % self.user


@python_2_unicode_compatible
class TaskLocation(models.Model):
    name = models.CharField(max_length=1024)
    venue = models.ForeignKey(Venue, null=True, blank=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class AbstractTaskTemplate(models.Model):
    class Meta:
        abstract = True

    MANDATORY_TASK_FIELDS = [
        'name', 'description', 'nbr_volunteers_min', 'nbr_volunteers_max',
    ]
    TASK_TEMPLATE_FIELDS = MANDATORY_TASK_FIELDS + ['category']

    name = models.CharField(max_length=1024, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey('TaskCategory', blank=True, null=True)

    nbr_volunteers_min = models.IntegerField(default=1, blank=True, null=True)
    nbr_volunteers_max = models.IntegerField(default=1, blank=True, null=True)

    def clean(self):
        super().clean()
        for field in self.MANDATORY_TASK_FIELDS:
            if not getattr(self, field):
                setattr(self, field, None)

        # Only keep fields that have been overridden from the template
        if hasattr(self, 'template') and self.template:
            for field in self.TASK_TEMPLATE_FIELDS:
                if getattr(self.template, field) == getattr(self, field):
                    setattr(self, field, None)

        # If TaskTemplate or Task without template, check mandatory fields
        if not hasattr(self, 'template') or not self.template:
            errors = {}
            for field in self.MANDATORY_TASK_FIELDS:
                if not getattr(self, field):
                    errors[field] = 'Your task needs a %s' % field
            if errors:
                raise ValidationError(errors)


@python_2_unicode_compatible
class TaskTemplate(AbstractTaskTemplate):
    """a template for a Task"""
    video_task = models.BooleanField(default=False)

    def __str__(self):
        return u'Template for %s' % self.name


class TaskQuerySet(models.QuerySet):
    @staticmethod
    def coalesce_from_template(field):
        return models.Func(
            models.F(field),
            models.F('template__%s' % field),
            function='coalesce',
        )

    def annotate_all(self):
        return self.select_related('template').annotate(
            nbr_volunteers=models.Count('volunteers'),
            min_volunteers=self.coalesce_from_template('nbr_volunteers_min'),
            max_volunteers=self.coalesce_from_template('nbr_volunteers_max'),
            name_=self.coalesce_from_template('name'),
            description_=self.coalesce_from_template('description'),
            category_=self.coalesce_from_template('category__name'),
        )


@python_2_unicode_compatible
class Task(AbstractTaskTemplate):
    """Something to do.

    If the template is set, it will override the name, description and
    category fields.
    """
    class Meta:
        ordering = ['start', '-end', 'template__name', 'name']

    objects = TaskQuerySet.as_manager()

    location = models.ForeignKey('TaskLocation', null=True)

    start = models.DateTimeField()
    end = models.DateTimeField()

    # Volunteers
    volunteers = models.ManyToManyField('Volunteer', blank=True)

    talk = models.ForeignKey(Talk, null=True, blank=True)
    template = models.ForeignKey(TaskTemplate, null=True, blank=True)

    def __str__(self):
        return u'%s (%s: %s - %s)' % (self.get_name(), self.start.date(),
                                      self.start.time(), self.end.time())

    def nbr_volunteers(self):
        return self.volunteer_set.count()
    nbr_volunteers.short_description = "# reg'd"

    def datetime(self):
        return u'%s: %s - %s' % (date(self.start.date(), 'l, F d'),
                                 date(self.start.time(), 'H:i'),
                                 date(self.end.time(), 'H:i'))

    def get_name(self):
        return self.name or self.template.name
    get_name.short_description = 'Name'

    def get_description(self):
        return self.description or self.template.description
    get_description.short_description = 'Description'

    def get_category(self):
        if not self.category:
            if self.template:
                return self.template.category

        return self.category
    get_category.short_description = 'Category'

    def get_nbr_volunteers_min(self):
        return self.nbr_volunteers_min or self.template.nbr_volunteers_min
    get_nbr_volunteers_min.short_description = '# min'

    def get_nbr_volunteers_max(self):
        return self.nbr_volunteers_max or self.template.nbr_volunteers_max
    get_nbr_volunteers_max.short_description = '# max'


@python_2_unicode_compatible
class TaskCategory(models.Model):
    """ Category of a task, like: cleanup, moderation, etc. """

    class Meta:
        verbose_name = _('task category')
        verbose_name_plural = _('task categories')

    name = models.CharField(max_length=1024)
    description = models.TextField()

    def __str__(self):
        return self.name
