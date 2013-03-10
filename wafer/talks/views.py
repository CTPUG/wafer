from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from wafer.talks.models import Talk
from wafer.talks.forms import TalkForm


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class TalkCreate(LoginRequiredMixin, CreateView):
    model = Talk
    form_class = TalkForm
    template_name = 'talks/submittalk.html'

    def form_valid(self, form):
        # Eaaargh we have to do the work of CreateView if we want to set values
        # before saving
        self.object = form.save(commit=False)
        self.object.corresponding_author = self.request.user
        self.object.save()
        #TODO: authors doesn't seem to be saving
        return HttpResponseRedirect(self.get_success_url())


class TalkUpdate(LoginRequiredMixin, UpdateView):
    model = Talk


class TalkDelete(LoginRequiredMixin, DeleteView):
    model = Talk
