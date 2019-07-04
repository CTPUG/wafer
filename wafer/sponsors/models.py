# -*- coding: utf-8 -*-

import logging

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from markitup.fields import MarkupField

from wafer.menu import menu_logger, refresh_menu_cache

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class File(models.Model):
    """A file for use in sponsor and sponshorship package descriptions."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    item = models.FileField(upload_to='sponsors_files')

    def __str__(self):
        return u'%s (%s)' % (self.name, self.item.url)


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
        File, related_name="packages", blank=True,
        help_text=_("Images and other files for use in"
                    " the description markdown field."))
    # We use purely ascii help text, to avoid issues with the migrations
    # not handling unicode help text nicely.
    symbol = models.CharField(
        max_length=1, blank=True,
        help_text=_("Optional symbol to display in the sponsors list "
                    "next to sponsors who have sponsored at this list, "
                    "(for example *)."))

    class Meta:
        ordering = ['order', '-price', 'name']

    def __str__(self):
        return u'%s (amount: %.0f)' % (self.name, self.price)

    def number_claimed(self):
        return self.sponsors.count()


@python_2_unicode_compatible
class Sponsor(models.Model):
    """A conference sponsor."""
    order = models.IntegerField(default=1)
    name = models.CharField(max_length=255)
    packages = models.ManyToManyField(SponsorshipPackage,
                                      related_name="sponsors")
    description = MarkupField(
        help_text=_("Write some nice things about the sponsor."))
    url = models.URLField(
        default="", blank=True,
        help_text=_("Url to link back to the sponsor if required"))

    class Meta:
        ordering = ['order', 'name', 'id']

    def __str__(self):
        return u'%s' % (self.name,)

    def get_absolute_url(self):
        return reverse('wafer_sponsor', args=(self.pk,))

    def symbols(self):
        """Return a string of the symbols of all the packages this sponsor has
           taken."""
        packages = self.packages.all()
        symbols = u"".join(p.symbol for p in packages)
        return symbols

    @property
    def symbol(self):
        """The symbol of the highest level package this sponsor has taken."""
        package = self.packages.first()
        if package:
            return package.symbol
        return u""


class TaggedFile(models.Model):
    """Tags for files associated with a given sponsor"""
    tag_name = models.CharField(max_length=255, null=False)
    tagged_file = models.ForeignKey(File, on_delete=models.CASCADE)
    sponsor = models.ForeignKey(Sponsor, related_name="files",
                                on_delete=models.CASCADE)


def sponsor_menu(
        root_menu, menu="sponsors", label=_("Sponsors"),
        sponsors_item=_("Our sponsors"),
        packages_item=_("Sponsorship packages")):
    """Add sponsor menu links."""
    root_menu.add_menu(menu, label, items=[])
    added_to_menu = set()
    for sponsor in (
            Sponsor.objects.all()
            .order_by('packages', 'order', 'id')
            .prefetch_related('packages')):
        if sponsor in added_to_menu:
            # We've already added this in a previous packaged
            continue
        added_to_menu.add(sponsor)
        symbols = sponsor.symbols()
        if symbols:
            item_name = u"» %s %s" % (sponsor.name, symbols)
        else:
            item_name = u"» %s" % (sponsor.name,)
        with menu_logger(logger, "sponsor %r" % (sponsor.name,)):
            root_menu.add_item(
                item_name, sponsor.get_absolute_url(), menu=menu)

    if sponsors_item:
        with menu_logger(logger, "sponsors page link"):
            root_menu.add_item(
                sponsors_item, reverse("wafer_sponsors"), menu)
    if packages_item:
        with menu_logger(logger, "sponsorship package page link"):
            root_menu.add_item(
                packages_item, reverse("wafer_sponsorship_packages"), menu)


post_save.connect(refresh_menu_cache, sender=Sponsor)
