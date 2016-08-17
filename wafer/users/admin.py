from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from wafer.users.models import UserProfile


# User-centric

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'
    exclude = ('kv',)


class UserAdmin(UserAdmin):
    inlines = (UserProfileInline,)


def username(obj):
    return obj.user.username


def email(obj):
    return obj.user.email


admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserAdmin)
