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


# UserProfile-centric (a hack, to customise KV Pairs)

class KVPairsInline(admin.StackedInline):
    model = UserProfile.kv.through
    verbose_name_plural = 'Key Value pairs'
    list_display = ('key', 'value')
    extra = 1


def username(obj):
    return obj.user.username


def email(obj):
    return obj.user.email


class UserProfileAdmin(admin.ModelAdmin):
    model = UserProfile
    readonly_fields = ('user',)
    exclude = ('kv',)
    inlines = (KVPairsInline,)
    list_select_related = ('user',)
    list_display = (username, 'display_name', email)
    search_fields = ('user__username', 'user__first_name', 'user__last_name',
                     'user__email')


admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserAdmin)

admin.site.register(UserProfile, UserProfileAdmin)
