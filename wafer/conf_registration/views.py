from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from wafer.conf_registration.models import Registration, RegisteredAttendee
from wafer.conf_registration.forms import RegistrationForm, AttendeeForm


class EditRegMixin(object):
    '''The user responsible for the registration can edit the details'''
    def get_object(self, *args, **kwargs):
        object_ = super(EditRegMixin, self).get_object(*args, **kwargs)
        username = self.request.user.username
        if (object_.registered_by.filter(username=username).exists()
                or self.request.user.is_staff):
            return object_
        else:
            raise PermissionDenied


class LoginRequiredMixin(object):
    '''Must be logged in'''
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class RegistrationView(DetailView):
    template_name = 'wafer.conf_registration/registration.html'
    model = Registration

    def get_object(self, *args, **kwargs):
        '''Only the person responsible for the registration, and staff, can
           see the full details'''
        object_ = super(RegistrationView, self).get_object(*args, **kwargs)
        username = self.request.user.username
        if (object_.registered_by.filter(username=username).exists()
                or self.request.user.is_staff):
            return object_
        else:
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super(RegistrationView, self).get_context_data(**kwargs)
        username = self.request.user.username
        context['can_edit'] = (
            self.object.registered_by.filter(username=username).exists()
            or self.request.user.is_staff)
        return context


class AttendeeView(DetailView):
    template_name = 'wafer.conf_registration/attendee.html'
    model = RegisteredAttendee

    def get_object(self, *args, **kwargs):
        '''Only the person responsible for the registration, and staff, can
           see the full details'''
        object_ = super(RegistrationView, self).get_object(*args, **kwargs)
        username = self.request.user.username
        if (object_.created_by.filter(username=username).exists()
                or self.request.user.is_staff):
            return object_
        else:
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super(RegistrationView, self).get_context_data(**kwargs)
        username = self.request.user.username
        context['can_edit'] = (
            self.object.created_by.filter(username=username).exists()
            or self.request.user.is_staff)
        return context


class AttendeeCreate(LoginRequiredMixin, CreateView):
    model = RegisteredAttendee
    form_class = AttendeeForm
    template_name = 'wafer.conf_registration/attendee_new.html'


class RegistrationCreate(LoginRequiredMixin, CreateView):
    model = Registration
    form_class = RegistrationForm
    template_name = 'wafer.conf_registration/reg_new.html'

    def form_valid(self, form):
        # self.object = form.save(commit=False)
        self.object.registered_by = self.request.user
        self.object.save()
        form.save_m2m()
        return HttpResponseRedirect(self.get_success_url())


class AttendeeUpdate(EditRegMixin, UpdateView):
    model = RegisteredAttendee
    form_class = AttendeeForm
    template_name = 'wafer.conf_registration/attendee_new.html'


class RegistrationUpdate(EditRegMixin, UpdateView):
    model = Registration
    form_class = RegistrationForm
    template_name = 'wafer.conf_registration/reg_new.html'


class AttendeeDelete(EditRegMixin, DeleteView):
    model = RegisteredAttendee
    template_name = 'wafer.conf_registration/attendee_delete.html'
    success_url = reverse_lazy('wafer_index')


class RegistrationCancel(EditRegMixin, DeleteView):
    model = Registration
    template_name = 'wafer.conf_registration/reg_cancel.html'
    success_url = reverse_lazy('wafer_index')
