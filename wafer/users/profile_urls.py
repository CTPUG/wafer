"""Configurable validation and rendering for user profile URLs."""

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.module_loading import import_string


def get_profile_callable(setting_name, field_name):
    """Load an optional callable configured by its dotted Python path."""
    configured = getattr(settings, setting_name, {})
    dotted_path = configured.get(field_name)

    if not dotted_path:
        return None

    return import_string(dotted_path)


def validate_rendered_url(renderer, value):
    """Ensure a renderer produces a valid HTTP or HTTPS URL."""
    try:
        url = renderer(value)
        URLValidator(schemes=["http", "https"])(url)
    except (ValidationError, TypeError, ValueError) as exc:
        raise ValidationError(
            "Enter a valid HTTP or HTTPS profile URL."
        ) from exc


def make_profile_field(category, field_name, label, initial=""):
    """Build a profile field with optional custom validation and rendering."""
    validator_setting = f"{category}_VALIDATORS"
    renderer_setting = f"{category}_RENDERERS"

    renderer = get_profile_callable(renderer_setting, field_name)
    custom_validator = get_profile_callable(validator_setting, field_name)

    validators = []
    if custom_validator:
        validators.append(custom_validator)

    if renderer:
        field = forms.CharField(
            label=label,
            max_length=1024,
            required=False,
            initial=initial,
            validators=validators,
        )
        field.validators.append(
            lambda value: validate_rendered_url(renderer, value)
            if value else None
        )
        return field

    return forms.URLField(
        label=label,
        max_length=1024,
        required=False,
        initial=initial,
        validators=validators,
    )


def render_profile_url(category, field_name, value):
    """Render a configured URL, rejecting invalid generated URLs."""
    if not value:
        return None

    renderer = get_profile_callable(
        f"{category}_RENDERERS", field_name
    )
    if not renderer:
        return value

    try:
        url = renderer(value)
        URLValidator(schemes=["http", "https"])(url)
    except (ValidationError, TypeError, ValueError):
        return None

    return url
