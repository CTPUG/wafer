import copy

from django.core.cache import cache
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import six

CACHE_KEY = "WAFER_MENU_CACHE"


def get_cached_menus():
    """Return the menus from the cache or generate them if needed."""
    items = cache.get(CACHE_KEY)
    if items is None:
        menu = generate_menu()
        cache.set(CACHE_KEY, menu.items)
    else:
        menu = Menu(items)
    return menu


def clear_menu_cache():
    """Clear the cached version of the menu (if any)."""
    cache.delete(CACHE_KEY)


def refresh_menu_cache(**kwargs):
    """Refresh the menu cache.

    Takes **kwargs to make it easier to use as a Django signal handler.
    """
    try:
        clear_menu_cache()
        get_cached_menus()
    except ObjectDoesNotExist as e:
        # During data loads, treat this as non-fatal, since we'll come back
        # here again with hopefully all the stuff required loaded eventually
        # (we use ObjectDoesNotExist to avoid awkard circular import issues)
        if not kwargs.get('raw'):
            raise e


def maybe_obj(str_or_obj):
    """If argument is not a string, return it.

    Otherwise import the dotted name and return that.
    """
    if not isinstance(str_or_obj, six.string_types):
        return str_or_obj
    parts = str_or_obj.split(".")
    mod, modname = None, None
    for p in parts:
        modname = p if modname is None else "%s.%s" % (modname, p)
        try:
            mod = __import__(modname)
        except ImportError:
            if mod is None:
                raise
            break
    obj = mod
    for p in parts[1:]:
        obj = getattr(obj, p)
    return obj


def generate_menu():
    """Generate a new list of menus."""
    root_menu = Menu(list(copy.deepcopy(settings.WAFER_MENUS)))
    for dynamic_menu_func in settings.WAFER_DYNAMIC_MENUS:
        dynamic_menu_func = maybe_obj(dynamic_menu_func)
        dynamic_menu_func(root_menu)
    return root_menu


class MenuError(Exception):
    """Raised when attempting illegal operations while constructiong menus."""


class Menu(object):
    """Utility class for manipulating a hierarchy of menus.

    A menu is maintained as a list of dictionaries (for ease of caching).

    Menu items are dictionaries with the keys: name, label and url. E.g.::

        {"name": "home", "label": _("Home"),
         "url": reverse("wafer_page", args=('index',))},

    Sub-menus are dictionaries with the keys: name, label and items.

        {"name": "sponsors", "label": _("Sponsors"),
         "items": [
             {"name": "sponsors", "label": _("Our sponsors"),
              "url": reverse("wafer_sponsors")},
             {"name": "packages", "label": _("Sponsorship packages"),
              "url": reverse("wafer_sponsorship_packages")},
         ]},

    Image button items can be adding an "image" key to the item.
    The label for the icon will be used as the alt-text for the image.

        {"name": "twitter", "label": _("Twitter"),
         "image": "/static/twitter.png",
         "url": "http://twitter.com/wafer"},

    """

    def __init__(self, items):
        self.items = items

    @staticmethod
    def mk_item(label, url, sort_key=None, image=None):
        return {"label": label, "url": url, "sort_key": sort_key,
                "image": image}

    @staticmethod
    def mk_menu(name, label, items, sort_key=None):
        return {"name": name, "label": label, "items": items,
                "sort_key": sort_key}

    def _descend_items(self, menu):
        menu_items = self.items
        if menu is not None:
            matches = [item for item in menu_items
                       if "items" in item and item.get("menu") == menu]
            if len(matches) != 1:
                raise MenuError("Unable to find sub-menu %r." % (menu,))
            menu_items = matches[0]["items"]
        return menu_items

    def add_item(self, label, url, menu=None, sort_key=None, image=None):
        menu_items = self._descend_items(menu)
        menu_items.append(self.mk_item(label, url, sort_key=sort_key,
            image=image))

    def add_menu(self, name, label, items, sort_key=None):
        self.items.append(self.mk_menu(name, label, items, sort_key=sort_key))
