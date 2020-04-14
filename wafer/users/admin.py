import json

from django.contrib import admin
from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _

from wafer.talks.models import render_author
from wafer.users.models import UserProfile


class AuthorAutocompleteView(AutocompleteJsonView):
    """We override the default so we can use render_author
       in the admin display"""

    def get(self, request, *args, **kwargs):
        """Override request to change the response object"""
        response = super().get(request, args, kwargs)
        # This isn't very efficient, but we don't want to duplicate
        # the specialised logic in AutocompleteJsonView either
        data = json.loads(response.content)
        if 'results' not in data:
            return response
        lookup = get_user_model().objects.get
        results = data['results']
        data['results'] = [{'id': x['id'],
                                'text': render_author(lookup(pk=int(x['id'])))}
                               for x in results]
        return JsonResponse(data)


# User-centric

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = _('profile')
    verbose_name_plural = _('profiles')
    exclude = ('kv',)


class UserAdmin(UserAdmin):
    inlines = (UserProfileInline,)

    def autocomplete_view(self, request):
        """Replace the autocomplete view for the users search widget"""
        return AuthorAutocompleteView.as_view(model_admin=self)(request)


def username(obj):
    return obj.user.username


def email(obj):
    return obj.user.email


admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserAdmin)
