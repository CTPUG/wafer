from django.conf import settings
from django.contrib.auth.mixins import (
    LoginRequiredMixin, PermissionRequiredMixin)
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q
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
from reversion.models import Version

from wafer.talks.models import (
    Review, Talk, TalkType, TalkUrl, Track,
    ACCEPTED, CANCELLED, SUBMITTED, UNDER_CONSIDERATION, WITHDRAWN)
from wafer.talks.forms import ReviewForm, get_talk_form_class
from wafer.talks.serializers import TalkSerializer, TalkUrlSerializer
from wafer.users.models import UserProfile
from wafer.utils import order_results_by, PaginatedBuildableListView


class EditOwnTalksMixin(object):
    '''Users can edit their own talks as long as the talk is
       "Under Consideration"'''
    def get_object(self, *args, **kwargs):
        object_ = super(EditOwnTalksMixin, self).get_object(*args, **kwargs)
        if object_.can_edit(self.request.user):
            return object_
        else:
            raise PermissionDenied


class UsersTalks(PaginatedBuildableListView):
    template_name = 'wafer.talks/talks.html'
    build_prefix = 'talks'
    paginate_by = 25

    @order_results_by('talk_type', 'talk_id')
    def get_queryset(self):
        # self.request will be None when we come here via the static site
        # renderer
        if (self.request and Talk.can_view_all(self.request.user)):
            return Talk.objects.all()
        return Talk.objects.filter(Q(status=ACCEPTED) |
                                   Q(status=CANCELLED))


class TalkView(BuildableDetailView):
    template_name = 'wafer.talks/talk.html'
    model = Talk

    # Needed so django-bakery only renders public talks
    def build_object(self, obj):
        """Override django-bakery to skip talks that raise 403"""
        try:
            super(TalkView, self).build_object(obj)
        except PermissionDenied:
            # We cleanup the directory created
            self.unbuild_object(obj)

    def create_request(self, path):
        request = super(TalkView, self).create_request(path)
        request.user = AnonymousUser()
        return request

    def get_object(self, *args, **kwargs):
        '''Only talk owners can see talks, unless they've been accepted'''
        object_ = super(TalkView, self).get_object(*args, **kwargs)
        if not object_.can_view(self.request.user):
            raise PermissionDenied
        return object_

    def render_to_response(self, *args, **kwargs):
        '''Canonicalize the URL if the slug changed'''
        if self.request.path != self.object.get_absolute_url():
            return HttpResponseRedirect(self.object.get_absolute_url())
        return super(TalkView, self).render_to_response(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TalkView, self).get_context_data(**kwargs)
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
        kwargs = super(TalkCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(TalkCreate, self).get_context_data(**kwargs)
        can_submit = getattr(settings, 'WAFER_TALKS_OPEN', True)
        if can_submit and TalkType.objects.exists():
            # Check for all talk types being disabled
            can_submit = TalkType.objects.filter(
                disable_submission=False).count() > 0
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
        kwargs = super(TalkUpdate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(TalkUpdate, self).get_context_data(**kwargs)
        context['can_edit'] = self.object.can_edit(self.request.user)
        return context

    @revisions.create_revision()
    def form_valid(self, form):
        revisions.set_user(self.request.user)
        revisions.set_comment("Talk Modified")
        return super(TalkUpdate, self).form_valid(form)


class TalkWithdraw(EditOwnTalksMixin, DeleteView):
    model = Talk
    template_name = 'wafer.talks/talk_withdraw.html'
    success_url = reverse_lazy('wafer_page')

    @revisions.create_revision()
    def delete(self, request, *args, **kwargs):
        """Override delete to only withdraw"""
        talk = self.get_object()
        talk.status = WITHDRAWN
        talk.save()
        revisions.set_user(self.request.user)
        revisions.set_comment("Talk Withdrawn")
        return HttpResponseRedirect(self.success_url)


class TalkReview(PermissionRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    permission_required = 'talks.add_review'
    template_name = 'wafer.talks/review_talk.html'

    def get_form_kwargs(self):
        kwargs = super(TalkReview, self).get_form_kwargs()
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
        with revisions.create_revision():
            response = super(TalkReview, self).form_valid(form)
            revisions.set_user(self.request.user)
            if existing:
                revisions.set_comment("Review Modified")
            else:
                revisions.set_comment("Review Created")

        # Because Review.save() was called before any scores were added,
        # the str() on the version would have had the previous total. Update.
        review = self.get_object()
        version = Version.objects.get_for_object(review).order_by('-pk').first()
        version.object_repr = str(review)
        version.save()

        talk = review.talk
        if talk.status == SUBMITTED:
            talk.status = UNDER_CONSIDERATION
            talk.save()

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
        context = super(Speakers, self).get_context_data(**kwargs)
        speakers = UserProfile.objects.filter(
            user__talks__status='A').distinct().prefetch_related(
                'user').order_by('user__first_name', 'user__last_name')
        context["speaker_rows"] = self._by_row(speakers, 4)
        return context


class TracksView(BuildableListView):
    model = Track
    template_name = 'wafer.talks/talk_tracks.html'
    build_path = 'talks/tracks/index.html'


class TalkTypesView(BuildableListView):
    model = TalkType
    template_name = 'wafer.talks/talk_types.html'
    build_path = 'talks/types/index.html'


class TalksViewSet(viewsets.ModelViewSet, NestedViewSetMixin):
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
            return Talk.objects.filter(Q(status=ACCEPTED) |
                                       Q(status=CANCELLED))
        elif Talk.can_view_all(self.request.user):
            return Talk.objects.all()
        else:
            # Also include talks owned by the user
            # XXX: Should this be all authors rather than just
            # the corresponding author?
            return Talk.objects.filter(
                Q(status=ACCEPTED) |
                Q(status=CANCELLED) |
                Q(corresponding_author=self.request.user))


class TalkExistsPermission(BasePermission):
    def has_permission(self, request, view):
        talk_id = view.get_parents_query_dict()['talk']
        if not Talk.objects.filter(pk=talk_id).exists():
            raise Http404
        return True


class TalkUrlsViewSet(viewsets.ModelViewSet, NestedViewSetMixin):
    """API endpoint that allows talks to be viewed or edited."""
    queryset = TalkUrl.objects.all().order_by('id')
    serializer_class = TalkUrlSerializer
    permission_classes = (DjangoModelPermissions, TalkExistsPermission)

    def create(self, request, *args, **kw):
        request.data['talk'] = self.get_parents_query_dict()['talk']
        return super(TalkUrlsViewSet, self).create(request, *args, **kw)

    def update(self, request, *args, **kw):
        request.data['talk'] = self.get_parents_query_dict()['talk']
        return super(TalkUrlsViewSet, self).update(request, *args, **kw)
