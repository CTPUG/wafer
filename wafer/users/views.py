from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, UpdateView
from django.views.generic.list import ListView
from django.contrib.auth import get_user_model

from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from wafer.users.forms import UserForm, UserProfileForm
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


class UserViewSet(viewsets.ModelViewSet):
    """API endpoint for users."""
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    # We want some better permissions than the default here, but
    # IsAdminUser will do for now.
    permission_classes = (IsAdminUser, )
