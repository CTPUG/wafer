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


def update_kv(kv, new_values, context):
    """Update a kv value with new values, but ensuring any
       pairs set that aren't accessible by the user are retained."""
    request = context.get('request', None)
    values = new_values
    if request.user.id is not None:
        grp_ids = [x.id for x in request.user.groups.all()]
        for existing in kv.all():
            if existing.group.id not in grp_ids:
                values.append(existing)
    # This is tedious, but we don't want to rebind kv
    kv.clear()
    for pair in values:
        kv.add(pair)
