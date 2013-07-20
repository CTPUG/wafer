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


class Page(models.Model):
    """An extra page for the site."""
    name = models.CharField(max_length=255)
    slug = models.SlugField(help_text=_("Last component of the page URL"))
    parent = models.ForeignKey('self', null=True, blank=True)
    content = MarkdownTextField(
        help_text=_("Markdown contents for the page."))
    menu = models.CharField(
        max_length=255,
        help_text=_("Dotted name of menu to put this page in."),
        blank=True, null=True, default=None)
    files = models.ManyToManyField(
        File, related_name="pages", null=True, blank=True,
        help_text=_("Images and other files for use in"
                    " the content markdown field."))

    def __unicode__(self):
        return u'%s' % (self.name,)

    def get_absolute_url(self):
        return reverse('wafer_page', args=(self.slug,))

    class Model:
        unique_together = (('parent', 'slug'),)


def page_menus(root_menu):
    """Add page menus."""
    for page in Page.objects.filter(menu__isnull=False):
        item_name = "%s.%s" % (page.menu, page.slug)
        try:
            root_menu.add_item(item_name, page.name, page.get_absolute_url())
        except MenuError, e:
            logger.error("Bad menu item %r for page with slug %r."
                         % (e, page.slug))


post_save.connect(refresh_menu_cache, sender=Page)
