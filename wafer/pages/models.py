import logging
logger = logging.getLogger(__name__)

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save

from wafer.snippets.markdown_field import MarkdownTextField
from wafer.menu import MenuError, refresh_menu_cache


class File(models.Model):
    """A file for use in page markup."""
    name = models.CharField(max_length=255)
    description = models.TextField()
    item = models.FileField(upload_to='pages_files')

    def __unicode__(self):
        return u'%s' % (self.name,)


class Page(models.Model):
    """An extra page for the site."""
    name = models.CharField(max_length=255)
    slug = models.SlugField(help_text=_("Last component of the page URL"))
    parent = models.ForeignKey('self', null=True, blank=True)
    content = MarkdownTextField(
        help_text=_("Markdown contents for the page."))
    include_in_menu = models.BooleanField(
        help_text=_("Whether to include in menus."),
        default=False)
    files = models.ManyToManyField(
        File, related_name="pages", null=True, blank=True,
        help_text=_("Images and other files for use in"
                    " the content markdown field."))

    def __unicode__(self):
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

    class Model:
        unique_together = (('parent', 'slug'),)


def page_menus(root_menu):
    """Add page menus."""
    for page in Page.objects.filter(include_in_menu=True):
        path = page.get_path()
        menu = path[0] if len(path) > 1 else None
        try:
            root_menu.add_item(page.name, page.get_absolute_url(), menu=menu)
        except MenuError, e:
            logger.error("Bad menu item %r for page with slug %r."
                         % (e, page.slug))


post_save.connect(refresh_menu_cache, sender=Page)
