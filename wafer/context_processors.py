from django.contrib.sites.models import get_current_site


def site_info(request):
    '''Expose the site's info to templates'''
    site = get_current_site(request)
    context = {
        'WAFER_CONFERENCE_NAME': site.name,
        'WAFER_BASE_URL': 'http://%s' % site.domain,
    }
    return context
