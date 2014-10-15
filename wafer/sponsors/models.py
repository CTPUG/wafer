from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from markitup.fields import MarkupField


@python_2_unicode_compatible
class File(models.Model):
    """A file for use in sponsor and sponshorship package descriptions."""
    name = models.CharField(max_length=255)
    description = models.TextField()
    item = models.FileField(upload_to='sponsors_files')

    def __str__(self):
        return u'%s' % (self.name,)


@python_2_unicode_compatible
class SponsorshipPackage(models.Model):
    """A description of a sponsorship package."""
    order = models.IntegerField(default=1)
    name = models.CharField(max_length=255)
    number_available = models.IntegerField(
        null=True, validators=[MinValueValidator(0)])
    currency = models.CharField(
        max_length=16, default='$',
        help_text=_("Currency symbol for the sponsorship amount."))
    price = models.DecimalField(
        max_digits=12, decimal_places=2,
        help_text=_("Amount to be sponsored."))
    short_description = models.TextField(
        help_text=_("One sentence overview of the package."))
    description = MarkupField(
        help_text=_("Describe what the package gives the sponsor."))
    files = models.ManyToManyField(
        File, related_name="packages", null=True, blank=True,
        help_text=_("Images and other files for use in"
                    " the description markdown field."))

    class Meta:
        ordering = ['order', '-price', 'name']

    def __str__(self):
        return u'%s (amount: %.0f)' % (self.name, self.price)


@python_2_unicode_compatible
class Sponsor(models.Model):
    """A conference sponsor."""
    name = models.CharField(max_length=255)
    packages = models.ManyToManyField(SponsorshipPackage,
                                      related_name="sponsors")
    description = MarkupField(
        help_text=_("Write some nice things about the sponsor."))
    files = models.ManyToManyField(
        File, related_name="sponsors", null=True, blank=True,
        help_text=_("Images and other files for use in"
                    " the description markdown field."))

    def __str__(self):
        return u'%s' % (self.name,)

    def get_absolute_url(self):
        return reverse('wafer_sponsor', args=(self.pk,))
