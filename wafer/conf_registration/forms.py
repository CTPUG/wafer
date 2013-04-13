from django import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.conf import settings

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML

from wafer.conf_registration.models import RegisteredAttendee

WAFER_WAITLIST_ON = getattr(settings, 'WAFER_WAITLIST_ON', False)
WAFER_REGISTRATION_OPEN = getattr(settings, 'WAFER_REGISTRATION_OPEN', False)
WAFER_REGISTRATION_LIMIT = getattr(settings, 'WAFER_REGISTRATION_LIMIT', 250)


class RegisteredAttendeeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(RegisteredAttendeeForm, self).__init__(*args, **kwargs)
        if not WAFER_WAITLIST_ON and WAFER_REGISTRATION_OPEN:
            self.fields['items'].required = True
        else:
            del self.fields['items']
        self.helper = FormHelper(self)
        submit_button = Submit('submit', _('Submit'))
        instance = kwargs['instance']
        if instance:
            self.helper.layout.append(
                    FormActions(
                        submit_button,
                        HTML('<a href="%s" class="btn btn-danger">%s</a>'
                            % (reverse('wafer_registration_cancel',
                                args=(instance.pk,)),
                                _('Cancel registration')))))
        else:
            self.helper.add_input(submit_button)

    class Meta:
        model = RegisteredAttendee
        exclude = ('registered_by', 'waitlist', 'waitlist_date')
