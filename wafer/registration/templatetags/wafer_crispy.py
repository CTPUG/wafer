from django import template
import sys

register = template.Library()


@register.assignment_tag
def wafer_form_helper(helper_name):
    '''
    Find the specified Crispy FormHelper and instantiate it.
    Handy when you are crispyifying other apps' forms.
    '''
    module, class_name = helper_name.rsplit('.', 1)
    if module not in sys.modules:
        __import__(module)
    mod = sys.modules[module]
    class_ = getattr(mod, class_name)
    return class_()
