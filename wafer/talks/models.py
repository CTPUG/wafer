from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.template.defaultfilters import slugify

from markitup.fields import MarkupField

from wafer.kv.models import KeyValue


# constants to make things clearer elsewhere
ACCEPTED = 'A'
PENDING = 'P'
REJECTED = 'R'
CANCELLED = 'C'

# Utility functions used in the forms
def render_author(author):
    return '%s (%s)' % (author.userprofile.display_name(), author)


@python_2_unicode_compatible
class TalkType(models.Model):
    """A type of talk."""
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=1024)
    order = models.IntegerField(default=1)
    disable_submission = models.BooleanField(default=False,
            help_text="Don't allow users to submit talks of this type.")

    def __str__(self):
        return u'%s' % (self.name,)

    class Meta:
        ordering = ['order', 'id']

    def css_class(self):
        """Return a string for use as a css class name"""
        # While css can represent complicated strings
        # using escaping, we want simplicity and obvious predictablity
        return u'talk-type-%s' % slugify(self.name)

    css_class.admin_order_field = 'name'
    css_class.short_description = 'CSS class name'


@python_2_unicode_compatible
class Talk(models.Model):

    class Meta:
        permissions = (
            ("view_all_talks", "Can see all talks"),
            ("edit_private_notes", "Can edit the private notes fields"),
        )

    TALK_STATUS = (
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Not Accepted'),
        (CANCELLED, 'Talk Cancelled'),
        (PENDING, 'Under Consideration'),
    )

    talk_id = models.AutoField(primary_key=True)
    talk_type = models.ForeignKey(TalkType, null=True)

    title = models.CharField(max_length=1024)

    abstract = MarkupField(
        help_text=_("Write two or three paragraphs describing your talk. "
                    "Who is your audience? What will they get out of it? "
                    "What will you cover?<br />"
                    "You can use Markdown syntax."))

    notes = models.TextField(
        null=True, blank=True,
        help_text=_("Any notes for the conference organisers?"))

    private_notes = models.TextField(
        null=True, blank=True,
        help_text=_("Note space for the conference organisers (not visible "
                    "to submitter)"))

    status = models.CharField(max_length=1, choices=TALK_STATUS,
                              default=PENDING)

    corresponding_author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='contact_talks',
        help_text=_(
            "The person submitting the talk (and who questions regarding the "
            "talk should be addressed to)."))

    authors = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='talks',
        help_text=_(
            "The speakers presenting the talk."))

    kv = models.ManyToManyField(KeyValue)

    def __str__(self):
        return u'%s: %s' % (self.corresponding_author, self.title)

    def get_absolute_url(self):
        return reverse('wafer_talk', args=(self.talk_id,))

    def get_corresponding_author_contact(self):
        email = self.corresponding_author.email
        profile = self.corresponding_author.userprofile
        if profile.contact_number:
            contact = profile.contact_number
        else:
            # Should we wrap this in a span for styling?
            contact = 'NO CONTACT INFO'
        return '%s - %s' % (email, contact)
    get_corresponding_author_contact.short_description = 'Contact Details'

    def get_corresponding_author_name(self):
        return render_author(self.corresponding_author)

    get_corresponding_author_name.admin_order_field = 'corresponding_author'
    get_corresponding_author_name.short_description = 'Corresponding Author'

    def get_authors_display_name(self):
        authors = list(self.authors.all())
        # Corresponding authors first
        authors.sort(
            key=lambda author: u'' if author == self.corresponding_author
                               else author.userprofile.display_name())
        names = [author.userprofile.display_name() for author in authors]
        if len(names) <= 2:
            return u' & '.join(names)
        return u'%s, et al.' % names[0]

    def get_in_schedule(self):
        if self.scheduleitem_set.all():
            return True
        return False

    get_in_schedule.short_description = 'Added to schedule'
    get_in_schedule.boolean = True

    def has_url(self):
        """Test if the talk has urls associated with it"""
        if self.talkurl_set.all():
            return True
        return False

    has_url.boolean = True

    # Helpful properties for the templates
    accepted = property(fget=lambda x: x.status == ACCEPTED)
    pending = property(fget=lambda x: x.status == PENDING)
    reject = property(fget=lambda x: x.status == REJECTED)
    cancelled = property(fget=lambda x: x.status == CANCELLED)

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
        if self.accepted:
            return True
        return False

    @classmethod
    def can_view_all(cls, user):
        return user.has_perm('talks.view_all_talks')

    def can_edit(self, user):
        if user.has_perm('talks.change_talk'):
            return True
        if self.pending:
            if self._is_among_authors(user):
                return True
        return False


class TalkUrl(models.Model):
    """An url to stuff relevant to the talk - videos, slides, etc.

       Note that these are explicitly not intended to be exposed to the
       user, but exist for use by the conference organisers."""

    description = models.CharField(max_length=256)
    url = models.URLField()
    talk = models.ForeignKey(Talk)
