from django.conf.urls import url

from wafer.volunteers.views import (TaskView, TasksView,
                                    VolunteerView, VolunteerUpdate)

urlpatterns = [
    url(r'^tasks/$', TasksView.as_view(), name='wafer_tasks'),
    url(r'^tasks/(?P<pk>\d+)/$', TaskView.as_view(), name='wafer_task'),
    url(r'^(?P<slug>[\w.@+-]+)/$', VolunteerView.as_view(),
        name='wafer_volunteer'),
    url(r'^(?P<slug>[\w.@+-]+)/update/$', VolunteerUpdate.as_view(),
        name='wafer_volunteer_update'),
]
