from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.shortcuts import redirect
from django.db.models import F, Count
from django import forms

from wafer.users.views import EditOneselfMixin
from wafer.volunteers.models import Volunteer, Task


class TasksView(ListView):
    model = Task
    template_name = 'wafer.volunteers/tasks.html'

    def get_queryset(self):
        return Task.objects.annotate(nbr_volunteers=Count('volunteers'))

    def get_context_data(self, **kwargs):
        context = super(TasksView, self).get_context_data(**kwargs)

        context['future_tasks'] = context['object_list'].filter(
            end__gte=timezone.now())
        context['volunteers_needed'] = context['future_tasks'].filter(
            nbr_volunteers__lt=F('nbr_volunteers_max'))

        if self.request.user.is_authenticated():
            try:
                volunteer = Volunteer.objects.get(user=self.request.user)
                context['preferred_tasks'] = context['volunteers_needed'].filter(
                    category__in=volunteer.preferred_categories.all(),
                )
            except Volunteer.DoesNotExist:
                pass

        return context


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


class VolunteerUpdateForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields = ['preferred_categories']
        widgets = {
            'preferred_categories': forms.SelectMultiple(
                attrs={'class': 'form-control'}
            )
        }


class VolunteerUpdate(EditOneselfMixin, UpdateView):
    model = Volunteer
    slug_field = 'user__username'
    form_class = VolunteerUpdateForm
    template_name = 'wafer.volunteers/volunteer_update.html'

    def get_success_url(self):
        return reverse('wafer_volunteer',
                       kwargs={'slug': self.object.user.username})
