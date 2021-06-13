import bleach
from bleach_allowlist import markdown_tags, markdown_attrs
from markdown import markdown


def bleached_markdown(text, **kwargs):
    """Try to avoid XSS by bleaching markdown output"""
    markdown_rendered = markdown(text, **kwargs)
    bleached = bleach.clean(markdown_rendered, markdown_tags, markdown_attrs)
    return bleached
