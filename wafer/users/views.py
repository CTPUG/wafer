from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import (
    ObjectDoesNotExist, PermissionDenied, ValidationError,
)
from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils.translation import ugettext as _
from django.views.generic import DetailView, UpdateView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from wafer.users.forms import (
    UserForm, UserProfileForm, get_registration_form_class,
)
from wafer.users.serializers import UserSerializer
from wafer.users.models import UserProfile


class UsersView(ListView):
    template_name = 'wafer.users/users.html'
    model = get_user_model()
    paginate_by = 25


class ProfileView(DetailView):
    template_name = 'wafer.users/profile.html'
    model = get_user_model()
    slug_field = 'username'
    slug_url_kwarg = 'username'


# TODO: Combine these
class EditOneselfMixin(object):
    def get_object(self, *args, **kwargs):
        object_ = super(EditOneselfMixin, self).get_object(*args, **kwargs)
        self.verify_edit_permission(object_)
        return object_

    def verify_edit_permission(self, object_):
        if hasattr(object_, 'user'):  # Accept User or UserProfile
            object_ = object_.user
        if object_ == self.request.user or self.request.user.is_staff:
            return
        else:
            raise PermissionDenied


class EditUserView(EditOneselfMixin, UpdateView):
    template_name = 'wafer.users/edit_user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    model = get_user_model()
    form_class = UserForm

    def get_success_url(self):
        return reverse('wafer_user_profile', args=(self.object.username,))


class EditProfileView(EditOneselfMixin, UpdateView):
    template_name = 'wafer.users/edit_profile.html'
    slug_field = 'user__username'
    slug_url_kwarg = 'username'
    model = UserProfile
    form_class = UserProfileForm

    def get_success_url(self):
        return reverse('wafer_user_profile', args=(self.object.user.username,))


class RegistrationView(EditOneselfMixin, FormView):
    template_name = 'wafer.users/registration.html'

    def get_user(self):
        return UserProfile.objects.get(user__username=self.kwargs['username'])

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

        initial = {}
        form = self.get_form_class()()
        for field in form.fields:
            try:
                initial[field] = saved.get(key=field).value
            except ObjectDoesNotExist:
                continue
        return initial

    def form_valid(self, form):
        if not settings.WAFER_REGISTRATION_OPEN:
            raise ValidationError(_('Registration is not open'))
        saved = self.get_queryset()
        user = self.get_user()
        group = self.get_kv_group()

        for key, value in form.cleaned_data.iteritems():
            try:
                pair = saved.get(key=key)
                pair.value = value
                pair.save()
            except ObjectDoesNotExist:
                user.kv.create(group=group, key=key, value=value)

        return super(RegistrationView, self).form_valid(form)

    def get_success_url(self):
        return reverse('wafer_user_profile', args=(self.kwargs['username'],))


class UserViewSet(viewsets.ModelViewSet):
    """API endpoint for users."""
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    # We want some better permissions than the default here, but
    # IsAdminUser will do for now.
    permission_classes = (IsAdminUser, )
