from django import forms
from django.utils.dateparse import parse_date, parse_datetime, parse_time


def deserialize_by_field(value, field):
    """
    Some types get serialized to JSON, as strings.
    If we know what they are supposed to be, we can deserialize them
    """
    if isinstance(field, forms.DateTimeField):
        value = parse_datetime(value)
    elif isinstance(field, forms.DateField):
        value = parse_date(value)
    elif isinstance(field, forms.TimeField):
        value = parse_time(value)
    return value
