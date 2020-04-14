from django.conf import settings
from django.core import validators
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.functional import lazy
from django.utils.text import format_lazy
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.timezone import now

import reversion
from markitup.fields import MarkupField
from reversion.models import Version

from wafer.kv.models import KeyValue


# constants to make things clearer elsewhere
SUBMITTED = 'S'
UNDER_CONSIDERATION = 'U'
PROVISIONAL = 'P'
ACCEPTED = 'A'
REJECTED = 'R'
CANCELLED = 'C'
WITHDRAWN = 'W'


# Utility functions used in the forms
# We define this here, rather than in the users model, to avoid import
# loops as we need to import talks into users
def render_author(author):
    return '%s (%s)' % (author.userprofile.display_name(), author)


def authors_help():
    _ = ugettext  # This function will be wrapped for lazy evaluation
    text = []
    text.append(_("The speakers presenting the talk."))
    if not settings.WAFER_PUBLIC_ATTENDEE_LIST:
        text.append(_(
            "To ensure attendee privacy, you will only be able to see "
            "yourself and authors that have been added to the talk by the "
            "conference organisers. "
            "If you will have other co-authors, add a note in the notes "
            "field, so the organisers can add them to your talk."
        ))
    text.append(_(
        "<strong>You, as the talk submitter, will be the talk's corresponding "
        "author.</strong>"
    ))
    return ' '.join(text)


class TalkTypeManager(models.Manager):

    def open_for_submission(self):
        Q = models.Q
        return self.filter(
            Q(disable_submission=False) &
            (
                Q(submission_deadline__isnull=True) |
                Q(submission_deadline__gt=now()) |
                Q(accept_late_submissions=True)
            )
        )


class TalkType(models.Model):
    """A type of talk."""
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), max_length=1024)
    order = models.IntegerField(_('order'), default=1)
    disable_submission = models.BooleanField(
        _('disable submission'),
        default=False,
        help_text="Don't allow users to submit talks of this type.")
    submission_deadline = models.DateTimeField(
        _('submission deadline'),
        null=True,
        blank=True,
        help_text=_("Deadline for submitting talks of this type")
    )
    accept_late_submissions = models.BooleanField(
        _('accept late submissions'),
        default=False,
        help_text=_("Whether submissions after the deadline should be accepted")
    )

    objects = TalkTypeManager()

    def __str__(self):
        return u'%s' % (self.name,)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = _('talk type')
        verbose_name_plural = _('talk types')

    def css_class(self):
        """Return a string for use as a css class name"""
        # While css can represent complicated strings
        # using escaping, we want simplicity and obvious predictablity
        return u'talk-type-%s' % slugify(self.name)

    css_class.admin_order_field = 'name'
    css_class.short_description = _('CSS class name')


class Track(models.Model):
    """A conference track."""
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), max_length=1024)
    order = models.IntegerField(_('order'), default=1)

    def __str__(self):
        return u'%s' % (self.name,)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = _('track')
        verbose_name_plural = _('tracks')

    def css_class(self):
        """Return a string for use as a css class name"""
        # While css can represent complicated strings
        # using escaping, we want simplicity and obvious predictablity
        return u'track-%s' % slugify(self.name)

    css_class.admin_order_field = 'name'
    css_class.short_description = _('CSS class name')


@reversion.register(follow=('urls',))
class Talk(models.Model):

    class Meta:
        permissions = (
            ("view_all_talks", "Can see all talks"),
            ("edit_private_notes", "Can edit the private notes fields"),
        )
        verbose_name = _('talk')
        verbose_name_plural = _('talks')

    TALK_STATUS = (
        (ACCEPTED, _('Accepted')),
        (REJECTED, _('Not accepted')),
        (CANCELLED, _('Cancelled')),
        (UNDER_CONSIDERATION, _('Under consideration')),
        (SUBMITTED, _('Submitted')),
        (PROVISIONAL, _('Provisionally Accepted')),
        (WITHDRAWN, _('Withdrawn')),
    )

    talk_id = models.AutoField(primary_key=True)
    talk_type = models.ForeignKey(
        TalkType, verbose_name=_("talk type"), null=True, blank=True, on_delete=models.SET_NULL)
    track = models.ForeignKey(
        Track, verbose_name=_("track"), null=True, blank=True, on_delete=models.SET_NULL)

    title = models.CharField(_("title"), max_length=1024)

    abstract = MarkupField(
        _("abstract"),
        help_text=_("Write two or three paragraphs describing your talk. "
                    "Who is your audience? What will they get out of it? "
                    "What will you cover?<br />"
                    "You can use Markdown syntax."))

    notes = models.TextField(
        _("notes"),
        null=True, blank=True,
        help_text=_(
            "Any notes for the conference? Such as additional background on "
            "the topic or presenters that isn't going to be published "
            "publicly, special requirements for the event, or thoughts on "
            "scheduling. These are not visible to the public."))

    private_notes = models.TextField(
        _("private notes"),
        null=True, blank=True,
        help_text=_("Note space for the conference organisers (not visible "
                    "to submitter)"))

    status = models.CharField(_('status'), max_length=1, choices=TALK_STATUS,
                              default=SUBMITTED)

    corresponding_author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='contact_talks',
        on_delete=models.CASCADE,
        verbose_name=_("corresponding author"),
        help_text=_(
            "The person submitting the talk (and who questions regarding the "
            "talk should be addressed to)."))

    authors = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='talks',
        verbose_name=_("authors"),
        help_text=lazy(authors_help, str))

    video = models.BooleanField(
        default=True,
        verbose_name=_("video"),
        help_text=format_lazy(_(
            "By checking this, you are giving permission for the talk to be "
            "videoed, and distributed by the conference, under the "
            '<a href="{license_url}">{license_name} license</a>.'),
            license_url=settings.WAFER_VIDEO_LICENSE_URL,
            license_name=settings.WAFER_VIDEO_LICENSE,
        ),
    )
    video_reviewer = models.EmailField(
        null=True, blank=True,
        verbose_name=_("video reviewer"),
        help_text=_(
            "Email address of a person who will be allowed to review "
            "and approve your video details. "
            "Ideally, a second set of eyes who is not a busy conference "
            "presenter. "
            "But you can specify yourself, if you can't think of anyone else "
            "who would care."
        ))

    kv = models.ManyToManyField(KeyValue)

    submission_time = models.DateTimeField(auto_now_add=True)

    @property
    def slug(self):
        return slugify(self.title)

    def __str__(self):
        return u'%s: %s' % (self.corresponding_author, self.title)

    def get_absolute_url(self):
        return reverse('wafer_talk', kwargs={
            'pk': self.talk_id,
            'slug': self.slug,
        })

    def get_corresponding_author_contact(self):
        email = self.corresponding_author.email
        profile = self.corresponding_author.userprofile
        if profile.contact_number:
            contact = profile.contact_number
        else:
            # Should we wrap this in a span for styling?
            contact = _('NO CONTACT INFO')
        return '%s - %s' % (email, contact)
    get_corresponding_author_contact.short_description = _('Contact Details')

    def get_corresponding_author_name(self):
        return render_author(self.corresponding_author)

    get_corresponding_author_name.admin_order_field = 'corresponding_author'
    get_corresponding_author_name.short_description = _('Corresponding Author')

    def get_authors_display_name(self):
        authors = list(self.authors.all())
        # Corresponding authors first
        authors.sort(
            key=lambda author: u'' if author == self.corresponding_author
                               else author.userprofile.display_name())
        names = [author.userprofile.display_name() for author in authors]
        if len(names) <= 2:
            return u' & '.join(names)
        return _(u'%s, et al.') % names[0]

    def get_in_schedule(self):
        if self.scheduleitem_set.all():
            return True
        return False

    get_in_schedule.short_description = _('Added to schedule')
    get_in_schedule.boolean = True

    def has_url(self):
        """Test if the talk has urls associated with it"""
        if self.urls.all():
            return True
        return False

    has_url.short_description = _('Has URL')
    has_url.boolean = True

    @property
    def is_late_submission(self):
        if self.talk_type and self.talk_type.submission_deadline:
            return self.submission_time > self.talk_type.submission_deadline
        else:
            return False

    @property
    def review_score(self):
        # Overridden in admin, to allow sorting
        reviews = [review.avg_score for review in self.reviews.all() if review.avg_score]
        if not reviews:
            return None
        return sum(reviews) / len(reviews)

    @property
    def review_count(self):
        # Overridden in admin, to allow sorting
        return self.reviews.all().count()

    # Helpful properties for the templates
    accepted = property(fget=lambda x: x.status == ACCEPTED)
    provisional = property(fget=lambda x: x.status == PROVISIONAL)
    submitted = property(fget=lambda x: x.status == SUBMITTED)
    under_consideration = property(
        fget=lambda x: x.status == UNDER_CONSIDERATION)
    reject = property(fget=lambda x: x.status == REJECTED)
    cancelled = property(fget=lambda x: x.status == CANCELLED)
    withdrawn = property(fget=lambda x: x.status == WITHDRAWN)

    def _is_among_authors(self, user):
        if self.corresponding_author.username == user.username:
            return True
        # not chaining with logical-or to avoid evaluation of the queryset
        return self.authors.filter(username=user.username).exists()

    def can_view(self, user):
        if user.has_perm('talks.view_all_talks'):
            return True
        if self._is_among_authors(user):
            return True
        if self.accepted or self.cancelled:
            return True
        return False

    @classmethod
    def can_view_all(cls, user):
        return user.has_perm('talks.view_all_talks')

    def can_edit(self, user):
        if user.has_perm('talks.change_talk'):
            return True
        if self.under_consideration or self.submitted:
            if self._is_among_authors(user):
                return True
        return False

    def can_review(self, user):
        return (user.has_perm('talks.add_review')
                and not self._is_among_authors(user))


@reversion.register()
class TalkUrl(models.Model):
    """An url to stuff relevant to the talk - videos, slides, etc.

       Note that these are explicitly not intended to be exposed to the
       user, but exist for use by the conference organisers."""

    description = models.CharField(max_length=256)
    url = models.URLField()
    talk = models.ForeignKey(Talk, related_name='urls',
                             on_delete=models.CASCADE)


@reversion.register(follow=('scores',))
class Review(models.Model):
    talk = models.ForeignKey(Talk, on_delete=models.CASCADE,
                             verbose_name=_('talk'),
                             related_name='reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 verbose_name=_('reviewer'),
                                 on_delete=models.CASCADE)

    notes = MarkupField(
        _('notes'),
        null=True, blank=True,
        help_text=_("Comments on the proposal (markdown)"))

    def __str__(self):
        return _(u'Review of %s by %s (%s)') % (
            self.talk.title, self.reviewer, self.avg_score)

    @property
    def avg_score(self):
        return self.scores.aggregate(total=models.Avg('value'))['total']

    def is_current(self):
        def last_updated(obj):
            version = Version.objects.get_for_object(obj).first()
            return version.revision.date_created
        return last_updated(self) >= last_updated(self.talk)

    is_current.boolean = True

    class Meta:
        unique_together = (('talk', 'reviewer'),)
        verbose_name = _('review')
        verbose_name_plural = _('reviews')


class ReviewAspect(models.Model):
    name = models.CharField(_('name'), max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('review aspect')
        verbose_name_plural = _('review aspects')


@reversion.register()
class Score(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               related_name='scores')
    aspect = models.ForeignKey(ReviewAspect, on_delete=models.CASCADE)

    value = models.IntegerField(default=0, validators=[
        validators.MinValueValidator(settings.WAFER_TALK_REVIEW_SCORES[0]),
        validators.MaxValueValidator(settings.WAFER_TALK_REVIEW_SCORES[1])
    ])

    def __str__(self):
        review = self.review
        return _(u'Review of %s by %s on %s: %i') % (
            review.reviewer, review.talk.title, self.aspect.name, self.value)

    class Meta:
        unique_together = (('review', 'aspect'),)
        verbose_name = _('score')
        verbose_name_plural = _('scores')
