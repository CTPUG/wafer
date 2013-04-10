from django import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML

from wafer.conf_registration.models import Registration, RegisteredAttendee


class RegistrationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
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
        model = Registration


class AttendeeForm(forms.ModelForm):

    class Meta:
        model = RegisteredAttendee
