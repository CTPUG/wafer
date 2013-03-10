from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, UpdateView
from django.views.generic.list import ListView

from wafer.users.forms import UserForm, UserProfileForm
from wafer.users.models import UserProfile


class UsersView(ListView):
    template_name = 'wafer.users/users.html'
    model = User
    paginate_by = 25


class ProfileView(DetailView):
    template_name = 'wafer.users/profile.html'
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'


# TODO: Combine these
class EditUserView(UpdateView):
    template_name = 'wafer.users/edit_user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    model = User
    form_class = UserForm

    def get_object(self, queryset=None):
        object_ = super(EditUserView, self).get_object(queryset)
        if object_ == self.request.user or self.request.user.is_staff:
            return object_
        else:
            raise PermissionDenied

    def get_success_url(self):
        return reverse('wafer_user_profile', args=(self.object.username,))


class EditProfileView(UpdateView):
    template_name = 'wafer.users/edit_profile.html'
    slug_field = 'user__username'
    slug_url_kwarg = 'username'
    model = UserProfile
    form_class = UserProfileForm

    def get_object(self, queryset=None):
        object_ = super(EditProfileView, self).get_object(queryset)
        if object_.user == self.request.user or self.request.user.is_staff:
            return object_
        else:
            raise PermissionDenied

    def get_success_url(self):
        return reverse('wafer_user_profile', args=(self.object.user.username,))
