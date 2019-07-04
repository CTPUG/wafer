# -*- coding: utf-8 -*-

"""Tests for wafer.sponsors models."""

from django.test import TestCase
from django.urls import reverse

from wafer.menu import get_cached_menus, Menu
from wafer.sponsors.models import SponsorshipPackage, Sponsor


def create_package(name, symbol, price, order=None):
    """Create a sponsor with the correct order if desired"""
    package = SponsorshipPackage.objects.create(
        name=name, symbol=symbol, price=price)
    if order:
        package.order = order
    return package


def create_sponsor(name, packages):
    """Create a sponsort with the given name and packages."""
    sponsor = Sponsor.objects.create(name=name)
    for name, symbol, price in packages:
        package = create_package(name, symbol, price)
        sponsor.packages.add(package)
    # We need to save here to trigger the menu rebuild with the right package info
    sponsor.save()
    return sponsor


def create_sponsor_in_existing_packages(name, packages):
    """Create a sponsor and add it to an existing package."""
    sponsor = Sponsor.objects.create(name=name)
    for package in packages:
        sponsor.packages.add(package)
    sponsor.save()
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
        """Test that a sponsor's symbol is retrieved properly when the sponsor
           has no packages."""
        sponsor = create_sponsor(u"Awesome Co", [])
        self.assertEqual(sponsor.symbol, u"")

    def test_sponsor_symbols_with_one_symbol(self):
        """Test that a sponsor's symbols are retrieved properly when there
           is one package with a symbol."""
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
        """Test that a sponsor's symbols are retrieved properly when the
           sponsor has no packages."""
        sponsor = create_sponsor(u"Awesome Co", [])
        self.assertEqual(sponsor.symbols(), u"")


class SponsorMenuTests(TestCase):

    def test_cached_menu(self):
        """Test that the default sponsor menu is generated correctly when
           a sponsor is added."""
        sponsor = create_sponsor(u"Awesome Co", [
            (u"Gold", u"*", 500),
        ])
        menu = get_cached_menus()
        self.assertEqual(menu.items, [
            Menu.mk_menu(u"sponsors", u"Sponsors", items=[
                Menu.mk_item(u"» Awesome Co *", sponsor.get_absolute_url()),
                Menu.mk_item(u"Our sponsors", reverse('wafer_sponsors')),
                Menu.mk_item(u"Sponsorship packages", reverse(
                    'wafer_sponsorship_packages')),
            ])
        ])

    def test_multiple_packages(self):
        """Test that multiple sponsors get ordered correctly."""
        gold_package = create_package(u"Gold", u"*", 500, 1)
        silver_package = create_package(u"Silver", u"+", 400, 2)
        bronze_package = create_package(u"Bronze", u"-", 300, 3)
        # We create 2 sponsors for each package, interleaving creation order""""
        sponsor1 = create_sponsor_in_existing_packages(u"Awesome1 Co", [gold_package])
        sponsor2 = create_sponsor_in_existing_packages(u"Awesome2 Co", [bronze_package])
        sponsor3 = create_sponsor_in_existing_packages(u"Awesome3 Co", [silver_package])
        sponsor4 = create_sponsor_in_existing_packages(u"Awesome4 Co", [bronze_package])
        sponsor5 = create_sponsor_in_existing_packages(u"Awesome5 Co", [silver_package])
        sponsor6 = create_sponsor_in_existing_packages(u"Awesome6 Co", [gold_package])
        # Sponsors in the menu should be sorted by package
        menu = get_cached_menus()
        self.assertEqual(menu.items, [
            Menu.mk_menu(u"sponsors", u"Sponsors", items=[
                Menu.mk_item(u"» Awesome1 Co *", sponsor1.get_absolute_url()),
                Menu.mk_item(u"» Awesome6 Co *", sponsor6.get_absolute_url()),
                Menu.mk_item(u"» Awesome3 Co +", sponsor3.get_absolute_url()),
                Menu.mk_item(u"» Awesome5 Co +", sponsor5.get_absolute_url()),
                Menu.mk_item(u"» Awesome2 Co -", sponsor2.get_absolute_url()),
                Menu.mk_item(u"» Awesome4 Co -", sponsor4.get_absolute_url()),
                Menu.mk_item(u"Our sponsors", reverse('wafer_sponsors')),
                Menu.mk_item(u"Sponsorship packages", reverse(
                    'wafer_sponsorship_packages')),
            ])
        ])

        # Test that changing the order field changes the ordering within the package
        sponsor1.order = 2
        sponsor3.order = 2
        # Ensure menus are regenerated
        sponsor1.save()
        sponsor3.save()

        menu = get_cached_menus()
        self.assertEqual(menu.items, [
            Menu.mk_menu(u"sponsors", u"Sponsors", items=[
                Menu.mk_item(u"» Awesome6 Co *", sponsor6.get_absolute_url()),
                Menu.mk_item(u"» Awesome1 Co *", sponsor1.get_absolute_url()),
                Menu.mk_item(u"» Awesome5 Co +", sponsor5.get_absolute_url()),
                Menu.mk_item(u"» Awesome3 Co +", sponsor3.get_absolute_url()),
                Menu.mk_item(u"» Awesome2 Co -", sponsor2.get_absolute_url()),
                Menu.mk_item(u"» Awesome4 Co -", sponsor4.get_absolute_url()),
                Menu.mk_item(u"Our sponsors", reverse('wafer_sponsors')),
                Menu.mk_item(u"Sponsorship packages", reverse(
                    'wafer_sponsorship_packages')),
            ])
        ])

    def test_single_sponsor_multiple_packages(self):
        """Test that a sponsor in multiple packages only gets shown once, but with all the symbols"""
        gold_package = create_package(u"Gold", u"*", 500, 1)
        silver_package = create_package(u"Silver", u"+", 400, 2)
        bronze_package = create_package(u"Bronze", u"-", 300, 3)
        # We create 2 sponsors for each package, interleaving creation order""""
        sponsor1 = create_sponsor_in_existing_packages(u"Awesome1 Co", [gold_package, bronze_package])
        sponsor2 = create_sponsor_in_existing_packages(u"Awesome2 Co", [bronze_package])
        sponsor3 = create_sponsor_in_existing_packages(u"Awesome3 Co", [silver_package, gold_package])
        sponsor4 = create_sponsor_in_existing_packages(u"Awesome4 Co", [bronze_package])
        sponsor5 = create_sponsor_in_existing_packages(u"Awesome5 Co", [silver_package])
        sponsor6 = create_sponsor_in_existing_packages(u"Awesome6 Co", [gold_package])
        # Sponsors in the menu should be sorted by package
        menu = get_cached_menus()
        self.assertEqual(menu.items, [
            Menu.mk_menu(u"sponsors", u"Sponsors", items=[
                Menu.mk_item(u"» Awesome1 Co *-", sponsor1.get_absolute_url()),
                Menu.mk_item(u"» Awesome3 Co *+", sponsor3.get_absolute_url()),
                Menu.mk_item(u"» Awesome6 Co *", sponsor6.get_absolute_url()),
                Menu.mk_item(u"» Awesome5 Co +", sponsor5.get_absolute_url()),
                Menu.mk_item(u"» Awesome2 Co -", sponsor2.get_absolute_url()),
                Menu.mk_item(u"» Awesome4 Co -", sponsor4.get_absolute_url()),
                Menu.mk_item(u"Our sponsors", reverse('wafer_sponsors')),
                Menu.mk_item(u"Sponsorship packages", reverse(
                    'wafer_sponsorship_packages')),
            ])
        ])
