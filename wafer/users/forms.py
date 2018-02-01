from django import forms
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.translation import ugettext as _

from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from wafer.users.models import UserProfile


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.include_media = False
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
        self.helper.include_media = False
        username = kwargs['instance'].user.username
        self.helper.form_action = reverse('wafer_user_edit_profile',
                                          args=(username,))
        self.helper['twitter_handle'].wrap(PrependedText,
                                           '@', placeholder=_('handle'))
        self.helper['github_username'].wrap(PrependedText,
                                            '@', placeholder=_('username'))
        self.helper.add_input(Submit('submit', _('Save')))

    class Meta:
        model = UserProfile
        exclude = ('user', 'kv')
