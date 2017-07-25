from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

from wafer.users.views import EditOneselfMixin
from wafer.volunteers.models import Volunteer, Task


class TasksView(ListView):
    model = Task
    template_name = 'wafer.volunteers/tasks.html'


class TaskView(DetailView):
    model = Task
    template_name = 'wafer.volunteers/task.html'

    def get_context_data(self, **kwargs):
        context = super(TaskView, self).get_context_data(**kwargs)
        # TODO Find a better way
        context['already_volunteer'] = (
            self.request.user.is_authenticated() and
            self.object.volunteers.filter(user=self.request.user).exists()
        )
        context['can_volunteer'] = (
            self.request.user.is_authenticated() and
            self.object.nbr_volunteers() < self.object.nbr_volunteers_max
        )
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseForbidden()
        self.object = self.get_object()
        volunteer, new = Volunteer.objects.get_or_create(user=request.user)

        if self.object in volunteer.tasks.all():
            volunteer.tasks.remove(self.object)
            self.object.volunteers.remove(volunteer)
        elif self.object.nbr_volunteers() < self.object.nbr_volunteers_max:
            volunteer.tasks.add(self.object)
            self.object.volunteers.add(volunteer)

        return redirect('wafer_task', pk=self.object.pk)


class VolunteerView(EditOneselfMixin, DetailView):
    model = Volunteer
    slug_field = 'user__username'
    template_name = 'wafer.volunteers/volunteer.html'

    def get_object(self, *args, **kwargs):
        # TODO Find a better way
        if self.request.user.is_authenticated():
            Volunteer.objects.get_or_create(user=self.request.user)

        return super(VolunteerView, self).get_object(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(VolunteerView, self).get_context_data(**kwargs)
        context['profile'] = self.object.user.userprofile
        return context


class VolunteerUpdate(EditOneselfMixin, UpdateView):
    model = Volunteer
    slug_field = 'user__username'
    fields = ['preferred_categories']
    template_name = 'wafer.volunteers/volunteer_update.html'

    def get_success_url(self):
        return reverse('wafer_volunteer',
                       kwargs={'slug': self.object.user.username})
