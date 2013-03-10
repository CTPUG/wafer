from django import forms
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from wafer.users.models import UserProfile


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        username = kwargs['instance'].username
        self.helper.form_action = reverse('wafer_user_edit',
                args=(username,))
        self.helper.add_input(Submit('submit', _('Save')))

    class Meta:
        # TODO: Password reset
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        username = kwargs['instance'].user.username
        self.helper.form_action = reverse('wafer_user_edit_profile',
                args=(username,))
        self.helper.add_input(Submit('submit', _('Save')))

    class Meta:
        model = UserProfile
        exclude = ('user',)
