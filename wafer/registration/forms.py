from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class RegistrationFormHelper(FormHelper):
    form_action = reverse('registration_register')

    def __init__(self, *args, **kwargs):
        super(RegistrationFormHelper, self).__init__(*args, **kwargs)
        self.add_input(Submit('submit', _('Sign up')))


class LoginFormHelper(FormHelper):
    form_action = settings.LOGIN_URL

    def __init__(self, *args, **kwargs):
        super(LoginFormHelper, self).__init__(*args, **kwargs)
        # TODO: next field
        self.add_input(Submit('submit', _('Log in')))
