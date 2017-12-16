# -*- coding: utf-8 -*-

"""Tests for wafer.sponsors models."""

from django.test import TestCase

from wafer.sponsors.models import SponsorshipPackage, Sponsor


def create_sponsor(name, packages):
    """Create a sponsort with the given name and packages."""
    sponsor = Sponsor.objects.create(name=name)
    for name, symbol, price in packages:
        package = SponsorshipPackage.objects.create(
            name=name, symbol=symbol, price=price)
        sponsor.packages.add(package)
    return sponsor


class SponsorTests(TestCase):

    def test_sponsor_symbol_with_symbol(self):
        """Test that a sponsor's symbol is retrieved properly when the package
           has a symbol."""
        sponsor = create_sponsor(u"Awesome Co", [
            (u"Gold", u"*", 500),
        ])
        self.assertEqual(sponsor.symbol, u"*")

    def test_sponsor_symbol_with_blank(self):
        """Test that a sponsor's symbol is retrieved properly when the package
           has no symbol."""
        sponsor = create_sponsor(u"Awesome Co", [
            (u"Gold", u"", 500),
        ])
        self.assertEqual(sponsor.symbol, u"")

    def test_sponsor_symbol_no_package(self):
        """Test that a sponsor's symbol is retrieved properly when the package
           has no symbol."""
        sponsor = create_sponsor(u"Awesome Co", [])
        self.assertEqual(sponsor.symbol, u"")

    def test_sponsor_symbols_with_one_symbol(self):
        """Test that a sponsor's symbols are retrieved properly when some
           packages have symbols."""
        sponsor = create_sponsor(u"Awesome Co", [
            (u"Gold", u"*", 500),
        ])
        self.assertEqual(sponsor.symbols(), u"*")

    def test_sponsor_symbols_with_multiple_symbols(self):
        """Test that a sponsor's symbols are retrieved properly when some
           packages have symbols."""
        sponsor = create_sponsor(u"Awesome Co", [
            (u"Gold", u"★", 500),
            (u"Silver", u"", 400),
            (u"Bronze", u"*", 300),
        ])
        self.assertEqual(sponsor.symbols(), u"★*")

    def test_sponsor_symbols_with_no_package(self):
        """Test that a sponsor's symbols are retrieved properly when some
           packages have symbols."""
        sponsor = create_sponsor(u"Awesome Co", [])
        self.assertEqual(sponsor.symbols(), u"")
