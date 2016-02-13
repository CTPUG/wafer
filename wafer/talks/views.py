from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.conf import settings
from django.shortcuts import get_object_or_404

from reversion import revisions
from rest_framework import viewsets, status
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.response import Response

from wafer.talks.models import Talk, ACCEPTED
from wafer.talks.forms import TalkForm
from wafer.talks.serializers import TalkSerializer
from wafer.users.models import UserProfile


class EditOwnTalksMixin(object):
    '''Users can edit their own talks as long as the talk is
       "Under Consideration"'''
    def get_object(self, *args, **kwargs):
        object_ = super(EditOwnTalksMixin, self).get_object(*args, **kwargs)
        if object_.can_edit(self.request.user):
            return object_
        else:
            raise PermissionDenied


class LoginRequiredMixin(object):
    '''Must be logged in'''
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class UsersTalks(ListView):
    template_name = 'wafer.talks/talks.html'
    paginate_by = 25

    def get_queryset(self):
        # self.request will be None when we come here via the static site
        # renderer
        if (self.request and Talk.can_view_all(self.request.user)):
            return Talk.objects.all()
        return Talk.objects.filter(status=ACCEPTED)


class TalkView(DetailView):
    template_name = 'wafer.talks/talk.html'
    model = Talk

    def get_object(self, *args, **kwargs):
        '''Only talk owners can see talks, unless they've been accepted'''
        object_ = super(TalkView, self).get_object(*args, **kwargs)
        if object_.can_view(self.request.user):
            return object_
        else:
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super(TalkView, self).get_context_data(**kwargs)
        context['can_edit'] = self.object.can_edit(self.request.user)
        return context


class TalkCreate(LoginRequiredMixin, CreateView):
    model = Talk
    form_class = TalkForm
    template_name = 'wafer.talks/talk_form.html'

    def get_form_kwargs(self):
        kwargs = super(TalkCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(TalkCreate, self).get_context_data(**kwargs)
        context['can_submit'] = getattr(settings, 'WAFER_TALKS_OPEN', True)
        return context

    @revisions.create_revision()
    def form_valid(self, form):
        if not getattr(settings, 'WAFER_TALKS_OPEN', True):
            raise ValidationError  # Should this be SuspiciousOperation?
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
    form_class = TalkForm
    template_name = 'wafer.talks/talk_form.html'

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


class TalkDelete(EditOwnTalksMixin, DeleteView):
    model = Talk
    template_name = 'wafer.talks/talk_delete.html'
    success_url = reverse_lazy('wafer_page', args=('index',))

    @revisions.create_revision()
    def form_valid(self, form):
        # We don't add any metadata, as the admin site
        # doesn't show it for deleted talks.
        return super(TalkDelete, self).form_valid(form)


class Speakers(ListView):
    model = Talk
    template_name = 'wafer.talks/speakers.html'

    def _by_row(self, speakers, n):
        return [speakers[i:i + n] for i in range(0, len(speakers), n)]

    def get_context_data(self, **kwargs):
        context = super(Speakers, self).get_context_data(**kwargs)
        speakers = UserProfile.objects.filter(
            user__talks__status='A').distinct().prefetch_related('user')
        context["speaker_rows"] = self._by_row(speakers, 4)
        return context


class TalksViewSet(viewsets.ModelViewSet):
    """API endpoint that allows talks to be viewed or edited."""
    queryset = Talk.objects.all()
    serializer_class = TalkSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )


    def list(self, request):
        # We override the default implementation to only show accepted talks
        # to people who aren't part of the management group
        if Talk.can_view_all(request.user):
            queryset = Talk.objects.all()
        else:
            # XXX: Should we also include talks owned by the user?
            queryset = Talk.objects.filter(status=ACCEPTED)
        serializer = TalkSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        # As above, but we allow people to see their own talks
        # as well
        queryset = Talk.objects.all()
        talk = get_object_or_404(queryset, pk=pk)
        if talk.can_view(request.user):
            serializer = TalkSerializer(talk)
            return Response(serializer.data)
        else:
            # Return denied
            data = {'detail': u'Permission denied'}
            return Response(data, status=status.HTTP_403_FORBIDDEN)
