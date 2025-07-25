from itertools import groupby

from django.conf import settings
from django.contrib.auth.mixins import (
    LoginRequiredMixin, PermissionRequiredMixin)
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q, F
from django.http import Http404
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from bakery.views import BuildableDetailView, BuildableListView
from rest_framework import viewsets
from rest_framework.permissions import (
    DjangoModelPermissions, DjangoModelPermissionsOrAnonReadOnly,
    BasePermission)
from rest_framework_extensions.mixins import NestedViewSetMixin
from reversion import revisions

from wafer.talks.models import (
    Review, Talk, TalkType, TalkUrl, Track,
    ACCEPTED, CANCELLED, PROVISIONAL, SUBMITTED, UNDER_CONSIDERATION,
    WITHDRAWN)
from wafer.talks.forms import ReviewForm, get_talk_form_class
from wafer.talks.serializers import TalkSerializer, TalkUrlSerializer, ReviewSerializer
from wafer.users.models import UserProfile
from wafer.utils import order_results_by, PaginatedBuildableListView


class EditOwnTalksMixin(object):
    '''Users can edit their own talks as long as the talk is
       "Under Consideration"'''
    def get_object(self, *args, **kwargs):
        object_ = super().get_object(*args, **kwargs)
        if object_.can_edit(self.request.user):
            return object_
        else:
            raise PermissionDenied


class UsersTalks(PaginatedBuildableListView):
    template_name = 'wafer.talks/talks.html'
    build_prefix = 'talks'
    paginate_by = 100

    def get_queryset(self):
        # self.request will be None when we come here via the static site
        # renderer
        if self.request and Talk.can_view_all(self.request.user):
            talks = Talk.objects.all()
        else:
            talks = Talk.objects.filter(
                Q(status__in=(ACCEPTED, CANCELLED))
                | Q(status__in=(SUBMITTED, UNDER_CONSIDERATION, PROVISIONAL),
                    talk_type__show_pending_submissions=True)
            )
        if self.request:
            if self.request.GET.get('sort') == 'track' and Track.objects.count() > 0:
                talks = talks.order_by('talk_type', 'track')
            elif self.request.GET.get('sort') == 'lang' and Talk.LANGUAGES:
                talks = talks.order_by('talk_type', 'language')
            elif self.request.GET.get('sort') == 'title':
                talks = talks.order_by('talk_type', 'title')
            else:
                talks = talks.order_by('talk_type', 'talk_id')
        else:
            talks = talks.order_by('talk_type', 'talk_id')
        return talks.prefetch_related(
            "talk_type", "corresponding_author", "authors", "authors__userprofile",
            "track"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["languages"] = Talk.LANGUAGES
        context["tracks"] = Track.objects.count() > 0
        context["see_all"] = Talk.can_view_all(self.request.user)
        context["includes_pending"] = TalkType.objects.filter(
            show_pending_submissions=True).exists()
        context['sort'] = self.request.GET.get('sort', 'default')
        return context


class TalkView(BuildableDetailView):
    template_name = 'wafer.talks/talk.html'
    model = Talk

    # Needed so django-bakery only renders public talks
    def build_object(self, obj):
        """Override django-bakery to skip talks that raise 403"""
        try:
            super().build_object(obj)
        except PermissionDenied:
            # We cleanup the directory created
            self.unbuild_object(obj)

    def create_request(self, path):
        request = super().create_request(path)
        request.user = AnonymousUser()
        return request

    def get_object(self, *args, **kwargs):
        '''Only talk owners can see talks, unless they've been accepted'''
        object_ = super().get_object(*args, **kwargs)
        if not object_.can_view(self.request.user):
            raise PermissionDenied
        return object_

    def canonical_url(self):
        '''Return the canonical URL for this view'''
        return self.object.get_absolute_url()

    def render_to_response(self, *args, **kwargs):
        '''Canonicalize the URL if the slug changed'''
        canonical_url = self.canonical_url()
        if self.request.path != canonical_url:
            return HttpResponseRedirect(canonical_url)
        return super().render_to_response(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        talk = self.object
        user = self.request.user

        context['can_edit'] = talk.can_edit(user)

        can_review = talk.can_review(user)
        context['can_review'] = can_review
        if can_review:
            review = talk.reviews.filter(reviewer=user).first()
            context['review_form'] = ReviewForm(
                instance=review, talk=talk, user=user)

        return context


class TalkCreate(LoginRequiredMixin, CreateView):
    model = Talk
    template_name = 'wafer.talks/talk_form.html'

    def get_form_class(self):
        return get_talk_form_class()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        can_submit = getattr(settings, 'WAFER_TALKS_OPEN', True)
        if can_submit and TalkType.objects.exists():
            # Check for all talk types being disabled
            can_submit = TalkType.objects.open_for_submission().count() > 0
        context['can_submit'] = can_submit
        return context

    @revisions.create_revision()
    def form_valid(self, form):
        if not getattr(settings, 'WAFER_TALKS_OPEN', True):
            # Should this be SuspiciousOperation?
            raise ValidationError("Talk submission isn't open")
        # Eaaargh we have to do the work of CreateView if we want to set values
        # before saving
        self.object = form.save(commit=False)
        self.object.corresponding_author = self.request.user
        self.object.save()
        revisions.set_user(self.request.user)
        revisions.set_comment("Talk Created")
        # Save the author information as well (many-to-many fun)
        form.save_m2m()
        return HttpResponseRedirect(self.get_success_url())


class TalkUpdate(EditOwnTalksMixin, UpdateView):
    model = Talk
    template_name = 'wafer.talks/talk_form.html'

    def get_form_class(self):
        return get_talk_form_class()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_edit'] = self.object.can_edit(self.request.user)
        return context

    @revisions.create_revision()
    def form_valid(self, form):
        revisions.set_user(self.request.user)
        revisions.set_comment("Talk Modified")
        return super().form_valid(form)


class TalkWithdraw(EditOwnTalksMixin, DeleteView):
    model = Talk
    template_name = 'wafer.talks/talk_withdraw.html'
    success_url = reverse_lazy('wafer_page')


    @revisions.create_revision()
    def withdraw_helper(self, request):
        """Handle the logic for withdrawing a talk"""
        talk = self.get_object()
        talk.status = WITHDRAWN
        talk.save()
        revisions.set_user(self.request.user)
        revisions.set_comment("Talk Withdrawn")
        return HttpResponseRedirect(self.success_url)

    def delete(self, request, *args, **kwargs):
        """Override delete to only withdraw for Django < 4"""
        return self.withdraw_helper(request)

    def form_valid(self, request, *args, **kwargs):
        """Override delete to only withdraw for Django >= 4.0"""
        return self.withdraw_helper(request)


class TalkReview(PermissionRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    permission_required = 'talks.add_review'
    template_name = 'wafer.talks/review_talk.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['talk'] = Talk.objects.get(pk=self.kwargs['pk'])
        kwargs['instance'] = self.get_object()
        kwargs['user'] = self.request.user
        return kwargs

    def get_object(self):
        try:
            return Review.objects.get(
                talk_id=self.kwargs['pk'], reviewer=self.request.user)
        except Review.DoesNotExist:
            return None

    def form_valid(self, form):
        existing = self.get_object()
        response = super().form_valid(form)

        review = self.get_object()
        # Update the talk to 'under consideration' if a review is
        # added.
        talk = review.talk
        if talk.status == SUBMITTED:
            talk.status = UNDER_CONSIDERATION
            with revisions.create_revision():
                revisions.set_user(self.request.user)
                revisions.set_comment("Status changed by review process")
                talk.save()

        # Create the revision
        # Note that we do this after the review has been saved
        # (without a revision) in the super().form_valid call and
        # after the scores have been added, so that the object_repr
        # is correct
        # We also do this after potentially updating the talk, so
        # that the review revision time is correct for is_current
        with revisions.create_revision():
            revisions.set_user(self.request.user)
            if existing:
                revisions.set_comment("Review Modified")
            else:
                revisions.set_comment("Review Created")
            review.save()

        return response

    def get_success_url(self):
        return self.get_object().talk.get_absolute_url()


class Speakers(BuildableListView):
    model = Talk
    template_name = 'wafer.talks/speakers.html'
    build_path = 'talks/speakers/index.html'

    def _by_row(self, speakers, n):
        return [speakers[i:i + n] for i in range(0, len(speakers), n)]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        speakers = UserProfile.objects.filter(
            user__talks__status='A').distinct().prefetch_related(
            'user').order_by('user__talks__talk_type',
                             'user__first_name',
                             'user__last_name',
                             'user__username').annotate(
            talk_type=F('user__talks__talk_type__name'),
            show_speakers=F('user__talks__talk_type__show_speakers'))
        bytype = groupby(speakers, lambda x: x.talk_type)
        context['speaker_rows'] = {}
        for talk_type, type_speakers in bytype:
            type_speakers = list(type_speakers)
            # We explicitly check for False, as no talk type will give us None for
            # show_speakers and we want to default to including that
            if type_speakers and type_speakers[0].show_speakers is not False:
                context["speaker_rows"][talk_type] = self._by_row(type_speakers, 4)
        return context


class TracksView(BuildableListView):
    model = Track
    template_name = 'wafer.talks/talk_tracks.html'
    build_path = 'talks/tracks/index.html'


class TalkTypesView(BuildableListView):
    model = TalkType
    template_name = 'wafer.talks/talk_types.html'
    build_path = 'talks/types/index.html'


class TalksViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    """API endpoint that allows talks to be viewed or edited."""
    queryset = Talk.objects.none()  # Needed for the REST Permissions
    serializer_class = TalkSerializer
    # XXX: Do we want to allow authors to edit talks via the API?
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )

    @order_results_by('talk_type', 'talk_id')
    def get_queryset(self):
        # We override the default implementation to only show accepted talks
        # to people who aren't part of the management group
        if self.request.user.id is None:
            # Anonymous user, so just accepted or cancelled talks
            return Talk.objects.filter(
                Q(status__in=(ACCEPTED, CANCELLED))
                | Q(status__in=(SUBMITTED, UNDER_CONSIDERATION, PROVISIONAL),
                    talk_type__show_pending_submissions=True)
            )
        elif Talk.can_view_all(self.request.user):
            return Talk.objects.all()
        else:
            # Also include talks owned by the user
            # XXX: Should this be all authors rather than just
            # the corresponding author?
            return Talk.objects.filter(
                Q(status__in=(ACCEPTED, CANCELLED))
                | Q(status__in=(SUBMITTED, UNDER_CONSIDERATION, PROVISIONAL),
                    talk_type__show_pending_submissions=True)
                | Q(corresponding_author=self.request.user)
            )


class TalkExistsPermission(BasePermission):
    def has_permission(self, request, view):
        talk_id = view.get_parents_query_dict()['talk']
        if not Talk.objects.filter(pk=talk_id).exists():
            raise Http404
        return True


class ReviewViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing all the reviews"""
    serializer_class = ReviewSerializer
    permission_classes = (DjangoModelPermissions, )

    @order_results_by('id')
    def get_queryset(self):
        if Review.can_view_all(self.request.user):
            # Only return the reviews for users with the correct permission
            return Review.objects.filter(talk_id=self.get_parents_query_dict()['talk'])
        return Review.objects.none()


class TalkUrlsViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    """API endpoint that allows talks to be viewed or edited."""
    queryset = TalkUrl.objects.all().order_by('id')
    serializer_class = TalkUrlSerializer
    permission_classes = (DjangoModelPermissions, TalkExistsPermission)

    def create(self, request, *args, **kw):
        request.data['talk'] = self.get_parents_query_dict()['talk']
        return super().create(request, *args, **kw)

    def update(self, request, *args, **kw):
        request.data['talk'] = self.get_parents_query_dict()['talk']
        return super().update(request, *args, **kw)
