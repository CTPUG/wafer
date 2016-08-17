import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import (
    ObjectDoesNotExist, PermissionDenied, ValidationError,
)
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render
from django.template import RequestContext, TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.views.generic import DetailView, UpdateView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from wafer.kv.utils import deserialize_by_field
from wafer.users.forms import (
    UserForm, UserProfileForm, get_registration_form_class,
)
from wafer.users.serializers import UserSerializer
from wafer.users.models import UserProfile

log = logging.getLogger(__name__)


class UsersView(ListView):
    template_name = 'wafer.users/users.html'
    model = get_user_model()
    paginate_by = 25

    def get_queryset(self, *args, **kwargs):
        if not settings.WAFER_PUBLIC_ATTENDEE_LIST:
            raise Http404()
        return super(UsersView, self).get_queryset(*args, **kwargs)


class ProfileView(DetailView):
    template_name = 'wafer.users/profile.html'
    model = get_user_model()
    slug_field = 'username'
    slug_url_kwarg = 'username'
    # avoid a clash with the user object used by the menus
    context_object_name = 'profile_user'

    def get_object(self, *args, **kwargs):
        object_ = super(ProfileView, self).get_object(*args, **kwargs)
        if not settings.WAFER_PUBLIC_ATTENDEE_LIST:
            if (not self.can_edit(object_) and
                    not object_.userprofile.accepted_talks().exists()):
                raise Http404()
        return object_

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context['can_edit'] = self.can_edit(context['object'])
        return context

    def can_edit(self, user):
        is_self = user == self.request.user
        return is_self or self.request.user.has_perm(
            'users.change_userprofile')


# TODO: Combine these
class EditOneselfMixin(object):
    def get_object(self, *args, **kwargs):
        object_ = super(EditOneselfMixin, self).get_object(*args, **kwargs)
        self.verify_edit_permission(object_)
        return object_

    def verify_edit_permission(self, object_):
        if hasattr(object_, 'user'):  # Accept User or UserProfile
            object_ = object_.user
        if object_ == self.request.user or self.request.user.has_perm(
                'users.change_userprofile'):
            return
        if settings.WAFER_PUBLIC_ATTENDEE_LIST:
            raise Http404()
        else:
            raise PermissionDenied()


class EditUserView(EditOneselfMixin, UpdateView):
    template_name = 'wafer.users/edit_user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    model = get_user_model()
    form_class = UserForm
    # avoid a clash with the user object used by the menus
    context_object_name = 'profile_user'

    def get_success_url(self):
        return reverse('wafer_user_profile', args=(self.object.username,))


class EditProfileView(EditOneselfMixin, UpdateView):
    template_name = 'wafer.users/edit_profile.html'
    slug_field = 'user__username'
    slug_url_kwarg = 'username'
    model = UserProfile
    form_class = UserProfileForm
    # avoid a clash with the user object used by the menus
    context_object_name = 'profile_user'

    def get_success_url(self):
        return reverse('wafer_user_profile', args=(self.object.user.username,))


class RegistrationView(EditOneselfMixin, FormView):
    template_name = 'wafer.users/registration/form.html'
    success_template_name = 'wafer.users/registration/success.html'
    confirm_mail_txt_template_name = (
        'wafer.users/registration/confirm_mail.txt')
    confirm_mail_html_template_name = (
        'wafer.users/registration/confirm_mail.html')

    def get_user(self):
        try:
            return UserProfile.objects.get(
                user__username=self.kwargs['username'])
        except UserProfile.DoesNotExist:
            raise Http404()

    def get_form_class(self):
        return get_registration_form_class()

    def get_kv_group(self):
        return Group.objects.get_by_natural_key('Registration')

    def get_queryset(self):
        if settings.WAFER_REGISTRATION_MODE != 'form':
            raise Http404('Form-based registration is not in use')
        user = self.get_user()
        self.verify_edit_permission(user)

        return user.kv.filter(group=self.get_kv_group())

    def get_initial(self):
        saved = self.get_queryset()

        form = self.get_form_class()()
        initial = form.initial_values(self.get_user())

        for fieldname in form.fields:
            try:
                value = saved.get(key=fieldname).value
                field = form.fields[fieldname]
                initial[fieldname] = deserialize_by_field(value, field)
            except ObjectDoesNotExist:
                continue
        return initial

    def form_invalid(self, form):
        log.info('User %s posted an incomplete registration form',
                 self.get_user().user.username)
        return super(RegistrationView, self).form_invalid(form)

    def form_valid(self, form):
        if not settings.WAFER_REGISTRATION_OPEN:
            raise ValidationError(_('Registration is not open'))
        saved = self.get_queryset()
        user = self.get_user()
        group = self.get_kv_group()

        for key, value in form.cleaned_data.items():
            try:
                pair = saved.get(key=key)
                pair.value = value
                pair.save()
            except ObjectDoesNotExist:
                user.kv.create(group=group, key=key, value=value)

        log.info('User %s successfully registered (%r)',
                 user.user.username, form.cleaned_data)

        is_registered = form.is_registered(self.get_queryset())
        send_email = (getattr(form, 'send_email_confirmation', False) and
                      is_registered)
        confirmation_context = self.get_confirmation_context_data(
            form, send_email, is_registered)
        context_instance = RequestContext(self.request, confirmation_context)
        if send_email:
            self.email_confirmation(context_instance)
        return self.confirmation_response(context_instance)

    def get_confirmation_context_data(self, form, will_send_email,
                                      is_registered):
        registration_data = []
        for fieldname, field in form.fields.items():
            registration_data.append({
                'name': fieldname,
                'label': field.label,
                'value': form.cleaned_data.get(fieldname),
            })

        context = self.get_context_data()
        context['form'] = form
        context['registered'] = is_registered
        context['registration_data'] = registration_data
        context['will_send_email'] = will_send_email
        context['talks_open'] = settings.WAFER_TALKS_OPEN
        return context

    def email_confirmation(self, context_instance):
        conference_name = get_current_site(self.request).name
        subject = _('%s Registration Confirmation') % conference_name
        txt = render_to_string(self.confirm_mail_txt_template_name,
                               context_instance=context_instance)
        try:
            html = render_to_string(self.confirm_mail_html_template_name,
                                    context_instance=context_instance)
        except TemplateDoesNotExist:
            html = None

        to = self.get_user().user.email
        email_message = EmailMultiAlternatives(subject, txt, to=[to])
        if html:
            email_message.attach_alternative(html, "text/html")
        email_message.send()

    def confirmation_response(self, context_instance):
        return render(self.request, self.success_template_name,
                      context_instance=context_instance)


class UserViewSet(viewsets.ModelViewSet):
    """API endpoint for users."""
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    # We want some better permissions than the default here, but
    # IsAdminUser will do for now.
    permission_classes = (IsAdminUser, )
