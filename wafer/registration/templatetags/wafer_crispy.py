from django import template
import sys

register = template.Library()


@register.simple_tag(takes_context=True)
def wafer_form_helper(context, helper_name):
    '''
    Find the specified Crispy FormHelper and instantiate it.
    Handy when you are crispyifying other apps' forms.
    '''
    request = context.request
    module, class_name = helper_name.rsplit('.', 1)
    if module not in sys.modules:
        __import__(module)
    mod = sys.modules[module]
    class_ = getattr(mod, class_name)
    return class_(request=request)
