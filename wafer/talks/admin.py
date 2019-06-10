from django.contrib import admin
from django import forms
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from reversion.admin import VersionAdmin
from easy_select2 import select2_modelform_meta

from wafer.compare.admin import CompareVersionAdmin, DateModifiedFilter
from wafer.talks.models import (
    Review, ReviewAspect, Score, Talk, TalkType, TalkUrl, Track, render_author)


class AdminTalkForm(forms.ModelForm):

    Meta = select2_modelform_meta(Talk)

    def __init__(self, *args, **kwargs):
        super(AdminTalkForm, self).__init__(*args, **kwargs)
        self.fields['authors'].label_from_instance = render_author
        self.fields['corresponding_author'].label_from_instance = render_author


class ScheduleListFilter(admin.SimpleListFilter):
    title = _('in schedule')
    parameter_name = 'schedule'

    def lookups(self, request, model_admin):
        return (
            ('in', _('Allocated to schedule')),
            ('out', _('Not allocated')),
            )

    def queryset(self, request, queryset):
        if self.value() == 'in':
            return queryset.filter(scheduleitem__isnull=False)
        elif self.value() == 'out':
            return queryset.filter(scheduleitem__isnull=True)
        return queryset


class HasNotesFilter(admin.SimpleListFilter):
    title = _('has notes')
    parameter_name = 'has_notes'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(notes__isnull=False).exclude(notes='')
        elif self.value() == 'no':
            return queryset.filter(Q(notes__isnull=True) | Q(notes=''))
        else:
            return queryset


class TalkUrlAdmin(VersionAdmin):
    list_display = ('description', 'talk', 'url')


class TalkUrlInline(admin.TabularInline):
    model = TalkUrl


class ReviewInline(admin.TabularInline):
    model = Review
    readonly_fields = ('reviewer', 'notes', 'avg_score', 'scores')
    extra = 0

    def scores(self, instance):
        output = []
        for score in instance.scores.all():
            output.append('{}: {}'.format(score.aspect.name, score.value))
        return ', '.join(output)

    def has_delete_permission(self, request, obj=None):
        return False


class TalkAdmin(CompareVersionAdmin):
    list_display = ('title', 'get_corresponding_author_name',
                    'get_corresponding_author_contact', 'talk_type',
                    'get_in_schedule', 'has_url', 'status',
                    'review_count', 'review_score')
    list_editable = ('status',)
    list_filter = ('status', 'talk_type', 'track', ScheduleListFilter,
                   DateModifiedFilter, HasNotesFilter,)
    search_fields = ('title',)
    exclude = ('kv',)

    inlines = [
        TalkUrlInline,
        ReviewInline,
    ]
    form = AdminTalkForm

    def get_queryset(self, request):
        qs = super(TalkAdmin, self).get_queryset(request)
        qs = qs.annotate(
            review_count_annotation=models.Count('reviews'),
            review_score_annotation=models.Avg('reviews__scores__value')
        )
        return qs

    def review_count(self, obj):
        return obj.review_count_annotation

    review_count.admin_order_field = 'review_count_annotation'

    def review_score(self, obj):
        return obj.review_score_annotation

    review_score.admin_order_field = 'review_score_annotation'


class TalkTypeAdmin(VersionAdmin):
    list_display = ('name', 'order', 'disable_submission', 'css_class')
    readonly_fields = ('css_class',)


class TrackAdmin(VersionAdmin):
    list_display = ('name', 'order', 'css_class')
    readonly_fields = ('css_class',)


class ReviewScoreInline(admin.TabularInline):
    model = Score


class ReviewAdmin(CompareVersionAdmin):
    list_display = ('talk', 'reviewer', 'avg_score', 'is_current')
    inlines = (ReviewScoreInline,)


admin.site.register(Review, ReviewAdmin)
admin.site.register(ReviewAspect)
admin.site.register(Talk, TalkAdmin)
admin.site.register(TalkType, TalkTypeAdmin)
admin.site.register(TalkUrl, TalkUrlAdmin)
admin.site.register(Track, TrackAdmin)
