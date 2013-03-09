'''
Created on 29 Jun 2012

@author: euan
'''
from django import forms

from pycon import models


class AttendeeRegistrationForm(forms.ModelForm):

    class Meta:
        model = models.AttendeeRegistration
        exclude = ('invoice_paid', 'on_waiting_list', 'active')

    def __init__(self, *args, **kwargs):

        self.base_fields['name'].widget.attrs.update({'class':
                                                      'required',
                                                      'tabindex': 1})
        self.base_fields['surname'].widget.attrs.update({'class':
                                                         'required',
                                                         'tabindex': 2})
        self.base_fields['contact_number'].widget.attrs.update({'tabindex': 3})
        self.base_fields['email'].widget.attrs.update({'class': 'required email',
                                                       'tabindex': 4})
        self.base_fields['registration_type'].widget.attrs.update({'class': 'required', 'tabindex': 5})

        super(AttendeeRegistrationForm, self).__init__(*args, **kwargs)


class SpeakerRegistrationForm(forms.ModelForm):

    class Meta:
        model = models.SpeakerRegistration

    def __init__(self, *args, **kwargs):

        self.base_fields['name'].widget.attrs.update({'class': 'required', 'tabindex': 1})
        self.base_fields['surname'].widget.attrs.update({'class': 'required', 'tabindex': 2})
        self.base_fields['contact_number'].widget.attrs.update({'tabindex': 5})
        self.base_fields['email'].widget.attrs.update({'class': 'required email', 'tabindex': 3})
        self.base_fields['bio'].widget.attrs.update({'class': 'required', 'tabindex': 5})
        self.base_fields['photo'].widget.attrs.update({'class': 'required', 'tabindex': 6})

        self.base_fields['talk_title'].widget.attrs.update({'class': 'required', 'tabindex': 7})
        self.base_fields['talk_type'].widget.attrs.update({'class': 'required', 'tabindex': 8})
        self.base_fields['talk_level'].widget.attrs.update({'class': 'required', 'tabindex': 9})
        self.base_fields['talk_category'].widget.attrs.update({'class': 'required', 'tabindex': 10})
        self.base_fields['talk_duration'].widget.attrs.update({'class': 'required', 'tabindex': 11})
        self.base_fields['talk_description'].widget.attrs.update({'class': 'required', 'tabindex': 12})
        self.base_fields['talk_abstract'].widget.attrs.update({'class': 'required', 'tabindex': 13})
        self.base_fields['talk_notes'].widget.attrs.update({'class': 'required', 'tabindex': 14})

        super(SpeakerRegistrationForm, self).__init__(*args, **kwargs)
