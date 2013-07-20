import datetime

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.timezone import utc
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.conf import settings

from wafer.conf_registration.models import RegisteredAttendee
from wafer.conf_registration.forms import RegisteredAttendeeForm


class EditRegMixin(object):
    '''The user responsible for the registration can edit the details'''
    def get_object(self, *args, **kwargs):
        object_ = super(EditRegMixin, self).get_object(*args, **kwargs)
        username = self.request.user.username
        if (object_.registered_by.username == username
                or self.request.user.is_staff):
            return object_
        else:
            raise PermissionDenied


class LoginRequiredMixin(object):
    '''Must be logged in'''
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class AttendeeView(DetailView):
    template_name = 'wafer.conf_registration/attendee.html'
    model = RegisteredAttendee

    def get_object(self, *args, **kwargs):
        '''Only the person responsible for the registration, and staff, can
           see the full details'''
        object_ = super(AttendeeView, self).get_object(*args, **kwargs)
        username = self.request.user.username
        if (object_.registered_by.username == username
                or self.request.user.is_staff):
            return object_
        else:
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super(AttendeeView, self).get_context_data(**kwargs)
        username = self.request.user.username
        context['can_edit'] = (
            self.object.registered_by.username == username
            or self.request.user.is_staff)
        return context


class AllAttendeeView(DetailView):
    template_name = 'wafer.conf_registration/all_attendee.html'
    model = RegisteredAttendee

    def get_object(self, *args, **kwargs):
        '''Only the person responsible for the registration, and staff, can
           see the full details'''
        user_id = self.request.user.pk
        if (RegisteredAttendee.objects.filter(
                registered_by_id=user_id).exists()):
            return RegisteredAttendee.objects.filter(
                    registered_by_id=user_id).all()
        else:
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super(AllAttendeeView, self).get_context_data(**kwargs)
        username = self.request.user.username
        user_id = self.request.user.pk
        context['can_edit'] = (RegisteredAttendee.objects.filter(
                registered_by_id=user_id).exists()
                or self.request.user.is_staff)
        context['username'] = username
        return context


class AttendeeCreate(LoginRequiredMixin, CreateView):
    model = RegisteredAttendee
    form_class = RegisteredAttendeeForm
    template_name = 'wafer.conf_registration/reg_new.html'

    def form_valid(self, form):
        WAFER_WAITLIST_ON = getattr(settings, 'WAFER_WAITLIST_ON', False)
        WAFER_REGISTRATION_OPEN = getattr(settings, 'WAFER_REGISTRATION_OPEN',
                False)
        WAFER_REGISTRATION_LIMIT = getattr(settings,
                'WAFER_REGISTRATION_LIMIT', 0)

        registered = RegisteredAttendee.objects.filter(waitlist=False)
        waitlist = (WAFER_WAITLIST_ON
                or (registered.count() >= WAFER_REGISTRATION_LIMIT and
                    WAFER_REGISTRATION_LIMIT > 0))
        reg_open = WAFER_REGISTRATION_OPEN
        if (not reg_open and not waitlist):
            # Closed
            raise PermissionDenied
        elif waitlist:
            # Add to waitlist
            self.object = form.save(commit=False)
            self.object.registered_by = self.request.user
            if self.request.user.get_full_name():
                self.object.name = self.request.user.get_full_name()
            else:
                self.object.name = self.request.user.username
            self.object.email = self.request.user.email
            self.object.waitlist = True
            # django.utils.timezone.now is neater, but 1.5 only
            now = datetime.datetime.utcnow().replace(tzinfo=utc)
            self.object.waitlist_date = now
            self.object.save()
        else:
            self.object = form.save(commit=False)
            self.object.registered_by = self.request.user
            self.object.save()
            form.save_m2m()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        WAFER_WAITLIST_ON = getattr(settings, 'WAFER_WAITLIST_ON', False)
        WAFER_REGISTRATION_OPEN = getattr(settings, 'WAFER_REGISTRATION_OPEN',
                False)
        WAFER_REGISTRATION_LIMIT = getattr(settings,
                'WAFER_REGISTRATION_LIMIT', 0)

        context = super(AttendeeCreate, self).get_context_data(**kwargs)
        registered = RegisteredAttendee.objects.filter(waitlist=False)
        context['waitlist'] = (WAFER_WAITLIST_ON
                or (registered.count() >= WAFER_REGISTRATION_LIMIT and
                    WAFER_REGISTRATION_LIMIT > 0))
        context['open'] = WAFER_REGISTRATION_OPEN
        return context


class AttendeeUpdate(EditRegMixin, UpdateView):
    model = RegisteredAttendee
    form_class = RegisteredAttendeeForm
    template_name = 'wafer.conf_registration/reg_new.html'


class AttendeeDelete(EditRegMixin, DeleteView):
    model = RegisteredAttendee
    template_name = 'wafer.conf_registration/reg_cancel.html'
    success_url = reverse_lazy('wafer_page', args=('index',))
