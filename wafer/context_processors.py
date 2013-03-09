from django.conf import settings


def expose_settings(request):
    '''Add some settings to the template's context'''
    context = {}
    for setting in ('YOUR_CONFERENCE_NAME',):
        context[setting] = getattr(settings, setting)
    return context
