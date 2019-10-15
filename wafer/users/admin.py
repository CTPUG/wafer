from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from wafer.users.models import UserProfile


# User-centric

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = _('profile')
    verbose_name_plural = _('profiles')
    exclude = ('kv',)


class UserAdmin(UserAdmin):
    inlines = (UserProfileInline,)


def username(obj):
    return obj.user.username


def email(obj):
    return obj.user.email


admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserAdmin)
