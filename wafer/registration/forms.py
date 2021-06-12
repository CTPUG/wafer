from django.conf import settings
from django.urls import reverse
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Hidden, Submit
from registration.forms import RegistrationForm

from wafer.registration.validators import validate_username


class WaferRegistrationForm(RegistrationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.include_media = False
        self.helper.form_action = reverse('registration_register')
        self.helper.add_input(Submit('submit', _('Sign up')))

    def clean_username(self):
        username = self.cleaned_data['username']
        validate_username(username)
        return username


class LoginFormHelper(FormHelper):
    form_action = settings.LOGIN_URL

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'next' in request.GET:
            self.add_input(Hidden('next', request.GET['next']))
        self.add_input(Submit('submit', _('Log in')))
