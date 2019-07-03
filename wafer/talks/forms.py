import copy

from django import forms
from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q
from django.urls import reverse
from django.utils.module_loading import import_string
from django.utils.translation import ugettext as _

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML
from easy_select2.widgets import Select2Multiple
from markitup.widgets import MarkItUpWidget

from wafer.talks.models import (
    Review, ReviewAspect, Score, Talk, TalkType, Track, render_author)


def get_talk_form_class():
    return import_string(settings.WAFER_TALK_FORM)


def has_field(model, field_name):
    try:
        model._meta.get_field(field_name)
        return True
    except FieldDoesNotExist:
        return False


class TalkCategorisationField(forms.ModelChoiceField):
    """The categories that talks can be placed into.
    These are always required, if there are any registered.
    """
    def __init__(self, model, initial=None, empty_label=None, *args, **kwargs):
        super(TalkCategorisationField, self).__init__(
            initial=initial,
            queryset=model.objects.all(),
            empty_label=None,
            required=True,
            *args, **kwargs)

        if has_field(model, 'disable_submission'):
            if initial:
                # Ensure the current selection is in the query_set, regardless
                # of whether it's been disabled since then
                self.queryset = self.queryset.filter(
                    Q(disable_submission=False) |
                    Q(pk=initial))
            else:
                self.queryset = self.queryset.filter(
                    disable_submission=False)

    def label_from_instance(self, obj):
        return u'%s: %s' % (obj.name, obj.description)


class TalkForm(forms.ModelForm):
    talk_type = TalkCategorisationField(model=TalkType)
    track = TalkCategorisationField(model=Track)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        initial = kwargs.setdefault('initial', {})
        if kwargs['instance']:
            authors = kwargs['instance'].authors.all()
        else:
            authors = initial['authors'] = [self.user]

        if not (settings.WAFER_PUBLIC_ATTENDEE_LIST
                or self.user.has_perm('talks.change_talk')):
            # copy base_fields because it's a shared class attribute
            self.base_fields = copy.deepcopy(self.base_fields)
            self.base_fields['authors'].limit_choices_to = {
                'id__in': [author.id for author in authors]}

        super(TalkForm, self).__init__(*args, **kwargs)

        if not self.user.has_perm('talks.edit_private_notes'):
            self.fields.pop('private_notes')

        if not Track.objects.exists():
            self.fields.pop('track')

        if not TalkType.objects.exists():
            self.fields.pop('talk_type')
        else:
            self.fields['talk_type'] = TalkCategorisationField(
                model=TalkType,
                initial=self.initial.get('talk_type')
            )

        if not settings.WAFER_VIDEO:
            self.fields.pop('video')
        if not settings.WAFER_VIDEO_REVIEWER:
            self.fields.pop('video_reviewer')

        # We add the name, if known, to the authors list
        self.fields['authors'].label_from_instance = render_author

        self.helper = FormHelper(self)
        self.helper.include_media = False
        submit_button = Submit('submit', _('Submit'))
        instance = kwargs['instance']
        if instance:
            self.helper.layout.append(
                FormActions(
                    submit_button,
                    HTML('<a href="%s" class="btn btn-danger">%s</a>'
                         % (reverse('wafer_talk_withdraw', args=(instance.pk,)),
                            _('Withdraw Talk')))))
        else:
            self.helper.add_input(submit_button)

    def clean_video_reviewer(self):
        video = self.cleaned_data['video']
        reviewer = self.cleaned_data['video_reviewer']
        if video and not reviewer:
            raise forms.ValidationError(
                _('A reviewer is required, if video is permitted.'))
        return reviewer

    class Meta:
        model = Talk
        fields = ('title', 'talk_type', 'track', 'abstract', 'authors',
                  'video', 'video_reviewer', 'notes', 'private_notes')
        widgets = {
            'abstract': MarkItUpWidget(),
            'notes': forms.Textarea(attrs={'class': 'input-xxlarge'}),
            'authors': Select2Multiple(),
        }


class ReviewForm(forms.Form):
    notes = forms.CharField(widget=MarkItUpWidget, required=False)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        self.talk = kwargs.pop('talk')
        self.user = kwargs.pop('user')

        if self.instance:
            kwargs['initial'] = {
                'notes': self.instance.notes.raw,
            }

        super(ReviewForm, self).__init__(*args, **kwargs)

        review_range  =_("(Score range: %(min)d to %(max)d)") % {
            'min': settings.WAFER_TALK_REVIEW_SCORES[0],
            'max': settings.WAFER_TALK_REVIEW_SCORES[1]
        }

        for aspect in ReviewAspect.objects.all():
            initial = None
            if self.instance:
                try:
                    initial = self.instance.scores.get(aspect=aspect).value
                except Score.DoesNotExist:
                    initial = None
            # We can't use label_suffix because we're going through crispy
            # forms, so we tack the range onto the label
            self.fields['aspect_{}'.format(aspect.pk)] = forms.IntegerField(
                initial=initial, label="%s %s" % (aspect.name, review_range),
                max_value=settings.WAFER_TALK_REVIEW_SCORES[1])

        self.helper = FormHelper(self)
        self.helper.form_action = reverse('wafer_talk_review',
                                          kwargs={'pk': self.talk.pk})
        self.helper.include_media = False
        self.helper.add_input(Submit('submit', _('Submit')))

    def save(self):
        review = self.instance
        if not review:
            review = Review(reviewer=self.user, talk=self.talk)
        review.notes = self.cleaned_data['notes']
        review.save()
        for aspect in ReviewAspect.objects.all():
            try:
                score = review.scores.get(aspect=aspect)
            except Score.DoesNotExist:
                score = Score(review=review, aspect=aspect)
            score.value = self.cleaned_data['aspect_{}'.format(aspect.pk)]
            score.save()
