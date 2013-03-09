'''Provide acccess to some settings in the django-registration email templates
'''
from django import template
from django.conf import settings

register = template.Library()


@register.assignment_tag
def wafer_conference_name():
    return settings.WAFER_CONFERENCE_NAME


@register.assignment_tag
def wafer_base_url():
    return settings.WAFER_BASE_URL
