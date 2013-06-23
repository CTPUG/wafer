from django.core.cache import cache

CACHE_KEY = "WAFER_MENU_CACHE"


def get_cached_menus():
    """Return the menus from the cache or generate them if needed."""
    menus = cache.get(CACHE_KEY)
    if menus is None:
        menus = generate_menus()
        cache.set(CACHE_KEY, menus)
    return menus


def clear_menu_cache():
    """Clear the cached version of the menu (if any)."""
    cache.delete(CACHE_KEY)


def generate_menus():
    """Generate a new list of menus."""
    return {}
