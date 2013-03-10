from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from wafer.talks.models import Talk
from wafer.talks.forms import TalkForm


class EditOwnTalksMixin(object):
    '''Users can edit their own talks unless the talk is finalised'''
    def get_object(self, *args, **kwargs):
        object_ = super(EditOwnTalksMixin, self).get_object(*args, **kwargs)
        username = self.request.user.username
        if ((object_.authors.filter(username=username).exists()
                    and not object_.finalised)
                or self.request.user.is_staff):
            return object_
        else:
            raise PermissionDenied


class LoginRequiredMixin(object):
    '''Must be logged in'''
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class TalkView(DetailView):
    template_name = 'wafer.talks/talk.html'
    model = Talk

    def get_object(self, *args, **kwargs):
        '''Only talk owners can see talks, unless they've been accepted'''
        object_ = super(TalkView, self).get_object(*args, **kwargs)
        username = self.request.user.username
        if (object_.authors.filter(username=username).exists()
                or self.request.user.is_staff
                or object_.accepted):
            return object_
        else:
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super(TalkView, self).get_context_data(**kwargs)
        username = self.request.user.username
        context['can_edit'] = (
            (self.object.authors.filter(username=username).exists()
                 and not self.object.finalised)
            or self.request.user.is_staff)
        return context


class TalkCreate(LoginRequiredMixin, CreateView):
    model = Talk
    form_class = TalkForm
    template_name = 'wafer.talks/talk_form.html'

    def form_valid(self, form):
        # Eaaargh we have to do the work of CreateView if we want to set values
        # before saving
        self.object = form.save(commit=False)
        self.object.corresponding_author = self.request.user
        self.object.save()
        #FIXME: authors doesn't seem to be saving on initial creation
        return HttpResponseRedirect(self.get_success_url())


class TalkUpdate(EditOwnTalksMixin, UpdateView):
    model = Talk
    form_class = TalkForm
    template_name = 'wafer.talks/talk_form.html'


class TalkDelete(EditOwnTalksMixin, DeleteView):
    model = Talk
    template_name = 'wafer.talks/talk_delete.html'
    success_url = reverse_lazy('wafer_index')
