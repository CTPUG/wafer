from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.forms import fields
from django.utils.module_loading import import_string
from django.utils.translation import ugettext as _

from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout, Submit

from wafer.users.models import UserProfile


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        username = kwargs['instance'].username
        self.helper.form_action = reverse('wafer_user_edit',
                                          args=(username,))
        self.helper.add_input(Submit('submit', _('Save')))
        self.fields['first_name'].required = True
        self.fields['email'].required = True

    class Meta:
        # TODO: Password reset
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email')


class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        username = kwargs['instance'].user.username
        self.helper.form_action = reverse('wafer_user_edit_profile',
                                          args=(username,))
        self.helper['twitter_handle'].wrap(PrependedText, 'twitter_handle',
                                           '@', placeholder=_('handle'))
        self.helper['github_username'].wrap(PrependedText, 'github_username',
                                            '@', placeholder=_('username'))
        self.helper.add_input(Submit('submit', _('Save')))

    class Meta:
        model = UserProfile
        exclude = ('user', 'kv')


def get_registration_form_class():
    return import_string(settings.WAFER_REGISTRATION_FORM)


class ExampleRegistrationForm(forms.Form):
    debcamp = fields.BooleanField(
        label=_('Plan to attend DebCamp'), required=False)
    debconf = fields.BooleanField(
        label=_('Plan to attend DebConf'), required=False)
    require_sponsorship = fields.BooleanField(
        label=_('Will require sponsorship'), required=False)

    def __init__(self, *args, **kwargs):
        super(ExampleRegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(_('Pre-Registration'),
                     'debcamp',
                     'debconf',
                     'require_sponsorship'))
        self.helper.add_input(Submit('submit', _('Save')))

    @classmethod
    def is_registered(cls, kv_data):
        """
        Given a user's kv_data query, determine if they have registered to
        attend.
        """
        for item in kv_data.filter(key__in=('debcamp', 'debconf')):
            if item.value is True:
                return True
        return False

    def initial_values(self, user):
        """Set default values, based on the user"""
        return {'debconf': True}
