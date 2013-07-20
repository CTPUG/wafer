import copy

from django.core.cache import cache
from django.conf import settings

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
    clear_menu_cache()
    get_cached_menus()


def maybe_obj(str_or_obj):
    """If argument is not a string, return it.

    Otherwise import the dotted name and return that.
    """
    if not isinstance(str_or_obj, basestring):
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
    root_menu = Menu(copy.deepcopy(settings.WAFER_MENUS))
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
    """

    def __init__(self, items):
        self.items = items

    @staticmethod
    def mk_item(name, label, url, sort_key=None):
        return {"name": name, "label": label, "url": url}

    @staticmethod
    def mk_menu(name, label, items, sort_key=None):
        return {"name": name, "label": label, "items": items}

    def _descend_items(self, parts):
        menu_items = self.items
        for sub_menu in parts:
            matches = [item for item in menu_items
                       if item["name"] == sub_menu and "items" in item]
            if len(matches) == 1:
                menu_items = matches[0]["items"]
            else:
                raise MenuError("Unable to find sub-menu %r of %r"
                                % (sub_menu, ".".join(parts)))
        return menu_items

    def add_item(self, name, label, url, sort_key=None):
        parts = name.split('.')
        menu_items = self._descend_items(parts[:-1])
        menu_items.append(self.mk_item(parts[-1], label, url))

    def add_menu(self, name, label, items):
        parts = name.split('.')
        menu_items = self._descend_items(parts[:-1])
        menu_items.append(self.mk_menu(parts[-1], label, items))
