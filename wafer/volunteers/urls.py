from django.conf.urls import url

from wafer.volunteers.views import (
    TaskView, TasksView, VideoMassScheduleView, VolunteerView, VolunteerUpdate,
)

urlpatterns = [
    url(r'^tasks/$', TasksView.as_view(), name='wafer_tasks'),
    url(r'^tasks/(?P<pk>\d+)/$', TaskView.as_view(), name='wafer_task'),
    url(r'^(?P<slug>[\w.@+-]+)/$', VolunteerView.as_view(),
        name='wafer_volunteer'),
    url(r'^(?P<slug>[\w.@+-]+)/update/$', VolunteerUpdate.as_view(),
        name='wafer_volunteer_update'),
    url(r'^admin/video_mass_schedule/$', VideoMassScheduleView.as_view())
]
