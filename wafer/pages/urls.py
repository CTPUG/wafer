from django.conf.urls import patterns, url

urlpatterns = patterns(
    'wafer.pages.views',
    url(r'^(.*)$', 'slug', name='wafer_page'),
)
