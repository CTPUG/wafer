from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from wafer.menu import get_cached_menus


def site_info(request):
    '''Expose the site's info to templates'''
    site = get_current_site(request)
    context = {
        'WAFER_CONFERENCE_NAME': site.name,
        'WAFER_CONFERENCE_DOMAIN': site.domain,
    }
    return context


def navigation_info(request):
    '''Expose whether to display the navigation header and footer'''
    if request.GET.get('wafer_hide_navigation') == "1":
        nav_class = "wafer-invisible"
    else:
        nav_class = "wafer-visible"
    context = {
        'WAFER_NAVIGATION_VISIBILITY': nav_class,
    }
    return context


def menu_info(request):
    '''Expose the menus to templates'''
    menus = get_cached_menus()
    context = {
        'WAFER_MENUS': menus,
    }
    return context


def registration_settings(request):
    '''Expose selected settings to templates'''
    context = {}
    for setting in (
            'WAFER_SSO',
            'WAFER_HIDE_LOGIN',
            'WAFER_REGISTRATION_OPEN',
            'WAFER_REGISTRATION_MODE',
            'WAFER_TALKS_OPEN',
            'WAFER_VIDEO_LICENSE',
    ):
        context[setting] = getattr(settings, setting, None)
    return context
