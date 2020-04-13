from django.test import TestCase


from wafer.menu import Menu
from wafer.pages.models import Page, page_menus


class PageMenusTests(TestCase):

    def test_simple_nested_menu(self):
        about = Page.objects.create(name='About', slug='about', include_in_menu=True)
        contact = Page.objects.create(name='Contact', slug='contact', include_in_menu=True, parent=about)
        menu = Menu([])
        page_menus(menu)
        self.assertEqual(menu.items, [
            Menu.mk_menu("about", "About", items=[
                Menu.mk_item("Contact", contact.get_absolute_url())
            ])
        ])

    def test_menu_ordering(self):
        schedule = Page.objects.create(name='Schedule', slug='schedule', include_in_menu=True, menu_order=20)
        about = Page.objects.create(name='About', slug='about', include_in_menu=True, menu_order=10)
        menu = Menu([])
        page_menus(menu)
        self.assertEqual(menu.items, [
            Menu.mk_item("About", about.get_absolute_url()),
            Menu.mk_item("Schedule", schedule.get_absolute_url()),
        ])
