from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.db import models

from wafer.snippets.markdown_field import MarkdownTextField


class File(models.Model):
    """A file for use in page markup."""
    name = models.CharField(max_length=255)
    description = models.TextField()
    item = models.FileField(upload_to='pages_files')


class Page(models.Model):
    """An extra page for the site."""
    name = models.CharField(max_length=255)
    content = MarkdownTextField(
        help_text=_("Markdown contents for the page."))
    files = models.ManyToManyField(
        File, related_name="pages", null=True, blank=True,
        help_text=_("Images and other files for use in"
                    " the content markdown field."))

    def __unicode__(self):
        return u'%s' % (self.name,)

    def get_absolute_url(self):
        return reverse('wafer_page', args=(self.pk,))
