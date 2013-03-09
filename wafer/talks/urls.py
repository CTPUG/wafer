from django.conf.urls.defaults import patterns, url

from wafer.talks.views import submit

urlpatterns = patterns('',
      url(r'^$', submit, name='talk_submit'),
      )
