import logging

from django.conf import settings
from django.core.cache import caches
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.db import models
from django.db.models.signals import post_save
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from markitup.fields import MarkupField, render_func

from wafer.menu import MenuError, refresh_menu_cache

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class File(models.Model):
    """A file for use in page markup."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    item = models.FileField(upload_to='pages_files')

    def __str__(self):
        return u'%s (%s)' % (self.name, self.item.url)


@python_2_unicode_compatible
class Page(models.Model):
    """An extra page for the site."""
    name = models.CharField(max_length=255)
    slug = models.SlugField(help_text=_("Last component of the page URL"))
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE)
    content = MarkupField(
        help_text=_("Markdown contents for the page."))
    include_in_menu = models.BooleanField(
        help_text=_("Whether to include in menus."),
        default=False)
    exclude_from_static = models.BooleanField(
        help_text=_("Whether to exclude this page from the static version of"
                    " the site (Container pages, etc.)"),
        default=False)
    files = models.ManyToManyField(
        File, related_name="pages", blank=True,
        help_text=_("Images and other files for use in"
                    " the content markdown field."))

    people = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='pages', blank=True,
        help_text=_("People associated with this page for display in the"
                    " schedule (Session chairs, panelists, etc.)"))

    cache_time = models.IntegerField(
        default=-1,
        help_text=_("Length of time (in seconds) to cache the page for "
                    "dynamic page content. A negative value means this page "
                    "is not dynamic and it will be not be regenerated "
                    "until it is next edited."))

    def __str__(self):
        return u'%s' % (self.name,)

    cache_name = settings.WAFER_CACHE

    def get_path(self):
        path, parent = [self.slug], self.parent
        while parent is not None:
            path.insert(0, parent.slug)
            parent = parent.parent
        return path

    def get_absolute_url(self):
        if self.slug == 'index' and not self.parent:
            return reverse('wafer_page')

        url = "/".join(self.get_path())
        return reverse('wafer_page', args=(url,))

    def _cache_key(self):
        return "wafer.pages:rendered:%s" % self.get_absolute_url()

    def cached_render(self):
        if self.cache_time < 0:
            return self.content.rendered
        cache = caches[self.cache_name]
        cache_key = self._cache_key()
        rendered = cache.get(cache_key)
        if rendered is None:
            rendered = render_func(self.content.raw)
            # Should reset the database copy, but this is enough for
            # now
            cache.set(cache_key, rendered, self.cache_time)
        return rendered

    def invalidate_cache(self):
        cache = caches[self.cache_name]
        cache.delete(self._cache_key())

    get_absolute_url.short_description = 'page url'

    def get_in_schedule(self):
        if self.scheduleitem_set.all():
            return True
        return False

    def get_people_display_names(self):
        names = [person.userprofile.display_name()
                 for person in self.people.all()]
        if len(names) > 2:
            comma_names = ', '.join(names[:-1])
            return comma_names + ' and ' + names[-1]
        else:
            return ' and '.join(names)

    get_in_schedule.short_description = 'Added to schedule'
    get_in_schedule.boolean = True

    get_people_display_names.short_description = 'People'

    class Model:
        unique_together = (('parent', 'slug'),)

    def clean(self):
        keys = [self.pk]
        parent = self.parent
        while parent is not None:
            if parent.pk in keys:
                raise ValidationError(
                    {
                        NON_FIELD_ERRORS: [
                            _("Circular reference in parent."),
                        ],
                    })
            keys.append(parent.pk)
            parent = parent.parent
        return super(Page, self).clean()

    def validate_unique(self, exclude=None):
        existing = Page.objects.filter(slug=self.slug, parent=self.parent)
        # We could be updating the page, so don't fail if the existing
        # entry is this page.
        if existing.count() > 1 or (existing.count() == 1 and
                                    existing.first().pk != self.pk):
            raise ValidationError(
                {
                    NON_FIELD_ERRORS: [
                        _("Duplicate parent/slug combination."),
                    ],
                })
        return super(Page, self).validate_unique(exclude)

    def save(self, *args, **kwargs):
        """Ensure we invalidate the cache after saving"""
        super(Page, self).save(*args, **kwargs)
        self.invalidate_cache()


def page_menus(root_menu):
    """Add page menus."""
    for page in Page.objects.filter(include_in_menu=True):
        path = page.get_path()
        menu = path[0] if len(path) > 1 else None
        try:
            root_menu.add_item(page.name, page.get_absolute_url(), menu=menu)
        except MenuError as e:
            logger.error("Bad menu item %r for page with slug %r."
                         % (e, page.slug))


post_save.connect(refresh_menu_cache, sender=Page)
