'''
Created on 29 Jun 2012

@author: euan
'''
from django import forms

from wafer import models


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
        self.base_fields['email'].\
            widget.attrs.update({'class': 'required email',
                                 'tabindex': 4})
        self.base_fields['registration_type'].\
            widget.attrs.update({'class': 'required', 'tabindex': 5})

        super(AttendeeRegistrationForm, self).__init__(*args, **kwargs)
