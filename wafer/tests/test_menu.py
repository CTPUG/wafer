# -*- coding: utf-8 -*-

"""Tests for wafer menu utilities."""

from django.test import TestCase

from wafer.menu import Menu


class MenuTests(TestCase):

    def test_mk_item_defaults(self):
        self.assertEqual(Menu.mk_item(
            u"My Label", u"http://example.com"
        ), {
            "label": u"My Label", "url": u"http://example.com",
            "sort_key": None, "image": None,
        })

    def test_mk_menu_defaults(self):
        self.assertEqual(Menu.mk_menu("my-menu", u"My Menu", []), {
            "menu": "my-menu", "label": u"My Menu",
            "items": [], "sort_key": None
        })
