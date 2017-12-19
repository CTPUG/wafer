# -*- coding: utf-8 -*-

"""Tests for wafer menu utilities."""

from django.test import TestCase

from wafer.menu import Menu, MenuError


class MenuTests(TestCase):

    def test_mk_item_defaults(self):
        self.assertEqual(Menu.mk_item(
            u"My Label", u"http://example.com"
        ), {
            "label": u"My Label", "url": u"http://example.com",
            "sort_key": None, "image": None,
        })

    def test_mk_item_overrides(self):
        self.assertEqual(Menu.mk_item(
            u"My Label", u"http://example.com",
            sort_key=1, image="/static/img/twitter.png"
        ), {
            "label": u"My Label", "url": u"http://example.com",
            "sort_key": 1, "image": "/static/img/twitter.png",
        })

    def test_mk_menu_defaults(self):
        self.assertEqual(Menu.mk_menu("my-menu", u"My Menu", []), {
            "menu": "my-menu", "label": u"My Menu",
            "items": [], "sort_key": None,
        })

    def test_mk_menu_overrides(self):
        self.assertEqual(Menu.mk_menu("my-menu", u"My Menu", [], sort_key=1), {
            "menu": "my-menu", "label": u"My Menu",
            "items": [], "sort_key": 1,
        })

    def test_add_item_to_root(self):
        menu = Menu([])
        menu.add_item(u"My Label", u"http://example.com")
        self.assertEqual(menu.items, [
            Menu.mk_item(u"My Label", u"http://example.com")
        ])

    def test_add_item_to_submenu(self):
        menu = Menu([
            Menu.mk_menu("my-menu", u"My Menu", [])
        ])
        menu.add_item(u"My Label", u"http://example.com", menu="my-menu")
        self.assertEqual(menu.items, [
            Menu.mk_menu("my-menu", u"My Menu", [
                Menu.mk_item(u"My Label", u"http://example.com")
            ])
        ])

    def test_add_item_to_nonexistent_submenu(self):
        menu = Menu([])
        with self.assertRaisesMessage(
                MenuError, "Unable to find sub-menu 'my-menu'."):
            menu.add_item(u"My Label", u"http://example.com", menu="my-menu")
        self.assertEqual(menu.items, [])

    def test_add_item_to_duplicated_submenus(self):
        menu = Menu([
            Menu.mk_menu("my-menu", u"My Menu 1", []),
            Menu.mk_menu("my-menu", u"My Menu 2", []),
        ])
        with self.assertRaisesMessage(
                MenuError, "Unable to find sub-menu 'my-menu'."):
            menu.add_item(u"My Label", u"http://example.com", menu="my-menu")
        self.assertEqual(menu.items, [
            Menu.mk_menu("my-menu", u"My Menu 1", []),
            Menu.mk_menu("my-menu", u"My Menu 2", []),
        ])

    def test_add_menu(self):
        menu = Menu([])
        menu.add_menu("my-menu", u"My Menu", [])
        self.assertEqual(menu.items, [
            Menu.mk_menu("my-menu", u"My Menu", [])
        ])

    def test_add_menu_exists(self):
        menu = Menu([])
        menu.add_menu("my-menu", u"My Menu", [
            Menu.mk_item(u"Item 1", u"http://example.com/1")
        ])
        menu.add_menu("my-menu", u"My Menu", [
            Menu.mk_item(u"Item 2", u"http://example.com/2")
        ])
        self.assertEqual(menu.items, [
            Menu.mk_menu("my-menu", u"My Menu", [
                Menu.mk_item(u"Item 1", u"http://example.com/1"),
                Menu.mk_item(u"Item 2", u"http://example.com/2"),
            ])
        ])

    def test_add_menu_multiple_exist(self):
        menu = Menu([
            Menu.mk_menu("my-menu", u"My Menu 1", []),
            Menu.mk_menu("my-menu", u"My Menu 2", []),
        ])
        with self.assertRaisesMessage(
                MenuError, "Multiple sub-menus named 'my-menu' exist."):
            menu.add_menu("my-menu", u"My Menu", [
                Menu.mk_item(u"Item 1", u"http://example.com/1"),
            ])
        self.assertEqual(menu.items, [
            Menu.mk_menu("my-menu", u"My Menu 1", []),
            Menu.mk_menu("my-menu", u"My Menu 2", []),
        ])
