# From http://djangosnippets.org/snippets/882/
# Copyright carljm (http://djangosnippets.org/users/carljm/)

from django.db.models import TextField
from markdown import markdown


class MarkdownTextField(TextField):
    """
    A TextField that automatically implements DB-cached Markdown translation.

    Accepts two additional keyword arguments:

    if allow_html is False, Markdown will be called in safe mode,
    which strips raw HTML (default is allow_html = True).

    if html_field_suffix is given, that value will be appended to the
    field name to generate the name of the non-editable HTML cache
    field.  Default value is "_html".

    NOTE: The MarkdownTextField is not able to check whether the model
    defines any other fields with the same name as the HTML field it
    attempts to add - if there are other fields with this name, a
    database duplicate column error will be raised.

    """
    def __init__(self, *args, **kwargs):
        self._markdown_safe = not kwargs.pop('allow_html', True)
        self._add_html_field = kwargs.pop('add_html_field', True)
        self._html_field_suffix = kwargs.pop('html_field_suffix', '_html')
        super(MarkdownTextField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        # During migrations, the column will already be in the new schema,
        # so we need to skip adding the column. The deconstruct serialization
        # will set _add_html_field to False for us in this case
        if self._add_html_field:
            self._html_field = "%s%s" % (name, self._html_field_suffix)
            TextField(editable=False).contribute_to_class(cls, self._html_field)
        super(MarkdownTextField, self).contribute_to_class(cls, name)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        html = markdown(value, safe_mode=self._markdown_safe)
        setattr(model_instance, self._html_field, html)
        return value

    def deconstruct(self):
        # Django 1.7 migration serializer
        name, path, args, kwargs = super(MarkdownTextField, self).deconstruct()
        kwargs['add_html_field'] = False
        kwargs['allow_html'] = self._markdown_safe
        kwargs['html_field_suffix'] = self._html_field_suffix
        return name, path, args, kwargs

    def __unicode__(self):
        return unicode(self.attname)

    def __str__(self):
        return self.attname
