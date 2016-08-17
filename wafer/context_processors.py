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
    ):
        context[setting] = getattr(settings, setting, None)
    return context
