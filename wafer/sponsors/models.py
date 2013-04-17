from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator
from django.db import models

from wafer.snippets.markdown_field import MarkdownTextField


class File(models.Model):
    """A file for use in sponsor and sponshorship package descriptions."""
    name = models.CharField(max_length=255)
    description = models.TextField()
    item = models.FileField(upload_to='sponsors_files')


class SponsorshipPackage(models.Model):
    """A description of a sponsorship package."""
    name = models.CharField(max_length=255)
    number_available = models.IntegerField(
        null=True, validators=[MinValueValidator(0)])
    price = models.DecimalField(max_digits=12, decimal_places=2)
    short_description = models.TextField(
        help_text=_("One sentence overview of the package."))
    description = MarkdownTextField(
        help_text=_("Describe what the package gives the sponsor."))
    files = models.ManyToManyField(
        File, related_name="packages",
        help_text=_("Images and other files for use in"
                    " the description markdown field."))

    def __unicode__(self):
        return u'%s (amount: %.f2)' % (self.name, self.price)


class Sponsor(models.Model):
    """A conference sponsor."""
    name = models.CharField(max_length=255)
    packages = models.ManyToManyField(SponsorshipPackage,
                                      related_name="sponsors")
    description = MarkdownTextField(
        help_text=_("Write some nice things about the sponsor."))
    files = models.ManyToManyField(
        File, related_name="sponsors",
        help_text=_("Images and other files for use in"
                    " the description markdown field."))

    def __unicode__(self):
        return u'%s' % (self.name,)

    def get_absolute_url(self):
        return reverse('wafer_sponsor', args=(self.pk,))
