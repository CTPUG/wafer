import logging
logger = logging.getLogger(__name__)

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.utils.encoding import python_2_unicode_compatible


from markitup.fields import MarkupField
from wafer.menu import MenuError, refresh_menu_cache


@python_2_unicode_compatible
class File(models.Model):
    """A file for use in page markup."""
    name = models.CharField(max_length=255)
    description = models.TextField()
    item = models.FileField(upload_to='pages_files')

    def __str__(self):
        return u'%s' % (self.name,)


@python_2_unicode_compatible
class Page(models.Model):
    """An extra page for the site."""
    name = models.CharField(max_length=255)
    slug = models.SlugField(help_text=_("Last component of the page URL"))
    parent = models.ForeignKey('self', null=True, blank=True)
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
        File, related_name="pages", null=True, blank=True,
        help_text=_("Images and other files for use in"
                    " the content markdown field."))

    people = models.ManyToManyField(settings.AUTH_USER_MODEL,
        related_name='pages', null=True, blank=True,
        help_text=_("People associated with this page for display in the"
                    " schedule (Session chairs, panelists, etc.)"))

    def __str__(self):
        return u'%s' % (self.name,)

    def get_path(self):
        path, parent = [self.slug], self.parent
        while parent is not None:
            path.insert(0, parent.slug)
            parent = parent.parent
        return path

    def get_absolute_url(self):
        url = "/".join(self.get_path())
        return reverse('wafer_page', args=(url,))

    def get_in_schedule(self):
        if self.scheduleitem_set.all():
            return True
        return False

    def get_people_display_names(self):
        names = []
        for person in self.people.all():
            full_name = person.get_full_name()
            if full_name:
                names.append(full_name)
            else:
                names.append(person.username)
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
