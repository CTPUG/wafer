from django.contrib import admin
from django import forms
from wafer.conf_registration.models import (
        ConferenceOption, ConferenceOptionGroup, RegisteredAttendee)


class ConferenceOptionGroupForm(forms.ModelForm):
    class Meta:
        model = ConferenceOptionGroup


class ConferenceOptionGroupAdmin(admin.ModelAdmin):
    form = ConferenceOptionGroupForm

admin.site.register(ConferenceOptionGroup, ConferenceOptionGroupAdmin)


class ConferenceOptionForm(forms.ModelForm):
    class Meta:
        model = ConferenceOption


class ConferenceOptionAdmin(admin.ModelAdmin):
    form = ConferenceOptionForm

admin.site.register(ConferenceOption, ConferenceOptionAdmin)


class AttendeeAdminForm(forms.ModelForm):
    class Meta:
        model = RegisteredAttendee

class AttendeeAdmin(admin.ModelAdmin):
    form = AttendeeAdminForm

admin.site.register(RegisteredAttendee, AttendeeAdmin)
