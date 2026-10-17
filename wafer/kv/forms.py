from django import forms
from django.contrib.auth.models import Group
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext as _

from wafer.kv.utils import deserialize_by_field


# Visibility levels for key-value backed form fields
PUBLIC = 'public'
REVIEWERS = 'reviewers'
ORGANISERS = 'organisers'


def build_kv_field(spec):
    """Turn a field specification (a plain dictionary, so it can live
       in settings) into a form field."""
    field_type = spec.get('type', 'char')
    kwargs = {
        'label': spec.get('label'),
        'required': spec.get('required', False),
        'help_text': spec.get('help_text', ''),
    }
    if field_type == 'boolean':
        return forms.BooleanField(**kwargs)
    elif field_type == 'char':
        return forms.CharField(max_length=spec.get('max_length', 1024),
                               **kwargs)
    elif field_type == 'text':
        return forms.CharField(widget=forms.Textarea, **kwargs)
    elif field_type == 'integer':
        return forms.IntegerField(**kwargs)
    elif field_type == 'url':
        return forms.URLField(max_length=1024, **kwargs)
    elif field_type == 'choice':
        choices = list(spec['choices'])
        if not kwargs['required']:
            choices.insert(0, ('', '---------'))
        return forms.ChoiceField(choices=choices, **kwargs)
    elif field_type == 'multiple_choice':
        return forms.MultipleChoiceField(
            choices=spec['choices'], widget=forms.CheckboxSelectMultiple,
            **kwargs)
    raise ValueError('Unknown key-value field type: %s' % field_type)


def kv_display_value(spec, value):
    """Render a stored value for display, using the choice labels where
       appropriate"""
    field_type = spec.get('type', 'char')
    if field_type == 'boolean':
        return _('Yes') if value else _('No')
    if field_type in ('choice', 'multiple_choice'):
        labels = dict(spec['choices'])
        if field_type == 'choice':
            return labels.get(value, value)
        return ', '.join(str(labels.get(x, x)) for x in value or [])
    return value


class KeyValueFieldsMixin:
    """Add extra fields to a ModelForm, which are stored as KeyValue
       pairs in the instance's kv field, rather than as model fields.

       Subclasses set kv_group_name, and either kv_fields or override
       get_kv_fields, which returns a dictionary mapping keys to field
       specifications (see build_kv_field)."""

    kv_group_name = None
    kv_fields = {}

    @classmethod
    def get_kv_fields(cls):
        return cls.kv_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        existing = {}
        if self.instance.pk:
            existing = {kv.key: kv.value for kv in self.instance.kv.filter(
                group__name=self.kv_group_name)}
        for key, spec in self.get_kv_fields().items():
            if key in self.fields:
                raise ImproperlyConfigured(
                    'Key-value field %s clashes with an existing form field'
                    % key)
            field = build_kv_field(spec)
            if key in existing:
                field.initial = deserialize_by_field(existing[key], field)
            self.fields[key] = field

    def _save_m2m(self):
        # Hooking in here means the key-value pairs are saved by both
        # form.save() and form.save(commit=False); form.save_m2m(),
        # after the instance has been saved.
        super()._save_m2m()
        kv_fields = self.get_kv_fields()
        if not kv_fields:
            return
        group, _created = Group.objects.get_or_create(name=self.kv_group_name)
        for key in kv_fields:
            if key not in self.cleaned_data:
                continue
            kv = self.instance.kv.filter(group=group, key=key).first()
            if kv:
                kv.value = self.cleaned_data[key]
                kv.save()
            else:
                self.instance.kv.create(group=group, key=key,
                                        value=self.cleaned_data[key])
