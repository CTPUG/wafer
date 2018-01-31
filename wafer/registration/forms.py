from django.conf import settings
from django.urls import reverse
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Hidden, Submit


class RegistrationFormHelper(FormHelper):
    form_action = reverse('registration_register')
    include_media = False

    def __init__(self, request, *args, **kwargs):
        super(RegistrationFormHelper, self).__init__(*args, **kwargs)
        self.add_input(Submit('submit', _('Sign up')))


class LoginFormHelper(FormHelper):
    form_action = settings.LOGIN_URL

    def __init__(self, request, *args, **kwargs):
        super(LoginFormHelper, self).__init__(*args, **kwargs)
        if 'next' in request.GET:
            self.add_input(Hidden('next', request.GET['next']))
        self.add_input(Submit('submit', _('Log in')))
