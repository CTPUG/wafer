import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.urls import reverse
from django.views.generic import UpdateView

from bakery.views import BuildableDetailView
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from wafer.talks.models import ACCEPTED
from wafer.users.forms import UserForm, UserProfileForm
from wafer.users.serializers import UserSerializer
from wafer.users.models import UserProfile
from wafer.utils import PaginatedBuildableListView

log = logging.getLogger(__name__)


class UsersView(PaginatedBuildableListView):
    template_name = 'wafer.users/users.html'
    model = get_user_model()
    paginate_by = 25
    build_prefix = 'users'

    def get_queryset(self, *args, **kwargs):
        qs = super(UsersView, self).get_queryset(*args, **kwargs)
        if not settings.WAFER_PUBLIC_ATTENDEE_LIST:
            qs = qs.filter(talks__status=ACCEPTED).distinct()
        qs = qs.order_by('first_name', 'last_name', 'username')
        return qs


class ProfileView(BuildableDetailView):
    template_name = 'wafer.users/profile.html'
    model = get_user_model()
    slug_field = 'username'
    slug_url_kwarg = 'username'
    # avoid a clash with the user object used by the menus
    context_object_name = 'profile_user'

    def get_url(self, obj):
        return reverse('wafer_user_profile', args=(obj.username,))

    def build_object(self, obj):
        """Override django-bakery to skip profiles that raise 404"""
        try:
            build_path = self.get_build_path(obj)
            self.request = self.create_request(build_path)
            self.request.user = AnonymousUser()
            self.set_kwargs(obj)
            self.build_file(build_path, self.get_content())
        except Http404:
            # cleanup directory
            self.unbuild_object(obj)

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


class UserViewSet(viewsets.ModelViewSet):
    """API endpoint for users."""
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    # We want some better permissions than the default here, but
    # IsAdminUser will do for now.
    permission_classes = (IsAdminUser, )
