from django import forms
from django.forms import fields
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
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


class ExampleRegistrationForm(forms.Form):
    debcamp = fields.BooleanField(
        label='Plan to attend DebCamp', required=False)
    debconf = fields.BooleanField(
        label='Plan to attend DebConf', required=False)
    require_sponsorship = fields.BooleanField(
        label='Will require sponsorship', required=False)

    def __init__(self, *args, **kwargs):
        super(ExampleRegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset('Pre-Registration',
                     'debcamp',
                     'debconf',
                     'require_sponsorship'))
        self.helper.add_input(Submit('submit', _('Save')))
