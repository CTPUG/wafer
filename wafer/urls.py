'''
Created on 29 Jun 2012

@author: euan
'''
from django.conf.urls.defaults import patterns, url
from django.views import generic as generic_views
from django.views.generic import RedirectView, TemplateView

from wafer import forms, models, views

urlpatterns = patterns('',

    url(r'^$',
        TemplateView.as_view(template_name='pycon/index.html'),
        name='index'),

    url(r'^index.html$',
        RedirectView.as_view(url='/'),
        name='index_redirect'),

    url(r'^about.html$',
        TemplateView.as_view(template_name='pycon/about.html'),
        name='about'),

    url(r'^venue.html$',
        TemplateView.as_view(template_name='pycon/venue.html'),
        name='venue'),

    url(r'^location.html$',
        TemplateView.as_view(template_name='pycon/location.html'),
        name='location'),

    url(r'^schedule.html$',
        TemplateView.as_view(template_name='pycon/schedule.html'),
        name='schedule'),

    url(r'^sponsors.html$',
        TemplateView.as_view(template_name='pycon/sponsors.html'),
        name='sponsors'),

    url(r'^sponsors_amazon.html$',
        TemplateView.as_view(template_name='pycon/sponsors_amazon.html'),
        name='sponsors_amazon'),

    url(r'^sponsors_google.html$',
        TemplateView.as_view(template_name='pycon/sponsors_google.html'),
        name='sponsors_google'),

    url(r'^sponsors_thoughtworks.html$',
        TemplateView.as_view(template_name='pycon/sponsors_thoughtworks.html'),
        name='sponsors_thoughtworks'),

    url(r'^sponsors_sjs.html$',
        TemplateView.as_view(template_name='pycon/sponsors_sjs.html'),
        name='sponsors_sjs'),

    url(r'^sponsors_psf.html$',
        TemplateView.as_view(template_name='pycon/sponsors_psf.html'),
        name='sponsors_psf'),

    url(r'^sponsors_basho.html$',
        TemplateView.as_view(template_name='pycon/sponsors_basho.html'),
        name='sponsors_basho'),

    url(r'^sponsors_praekelt_foundation.html$',
        TemplateView.as_view(template_name='pycon/sponsors_praekelt_foundation.html'),
        name='sponsors_praekelt_foundation'),

    url(r'^sponsors_information_logistics.html$',
        TemplateView.as_view(template_name='pycon/sponsors_information_logistics.html'),
        name='sponsors_information_logistics'),

    url(r'^sponsors_clickatell.html$',
        TemplateView.as_view(template_name='pycon/sponsors_clickatell.html'),
        name='sponsors_clickatell'),

    url(r'^sponsors_packages.html$',
        TemplateView.as_view(template_name='pycon/sponsors_packages.html'),
        name='sponsors_packages'),

    url(r'^contact.html$',
        TemplateView.as_view(template_name='pycon/contact.html'),
        name='contact'),

    url(r'^register.html$',
        views.RegisterView.as_view(form_class=forms.AttendeeRegistrationForm,
                                   template_name='pycon/register.html',
                                   success_url='/register_thanks.html'),
        name='register'),

    url(r'^register_thanks.html$',
        TemplateView.as_view(template_name='pycon/register_thanks.html'),
        name='register_thanks'),

    url(r'^speaker.html$',
        generic_views.CreateView.as_view(
            form_class=forms.SpeakerRegistrationForm,
            template_name='pycon/speaker.html',
            success_url='/speaker_thanks.html'),
        name='speaker'),

    url(r'^speaker_thanks.html$',
        TemplateView.as_view(template_name='pycon/speaker_thanks.html'),
        name='speaker_thanks'),

    url(r'^invoice/(.*)/$',
        views.attendee_invoice,
        name='attendee_invoice'),

    url(r'^book.html$',
        TemplateView.as_view(template_name='pycon/book.html'),
        name='book'),

    url(r'^book_thanks.html$',
        TemplateView.as_view(template_name='pycon/book_thanks.html'),
        name='book_thanks'),

    url(r'^news.html$',
        TemplateView.as_view(template_name='pycon/news.html'),
        name='news'),

    url(r'^news_pr1.html$',
        TemplateView.as_view(template_name='pycon/news_pr1.html'),
        name='news_pr1'),

    url(r'^news_umbono.html$',
        TemplateView.as_view(template_name='pycon/news_umbono.html'),
        name='news_umbono'),

    url(r'^news_umonya.html$',
        TemplateView.as_view(template_name='pycon/news_umonya.html'),
        name='news_umonya'),

    url(r'^news_3weeks.html$',
        TemplateView.as_view(template_name='pycon/news_3weeks.html'),
        name='news_3weeks'),

    url(r'^news_sponsors.html$',
        TemplateView.as_view(template_name='pycon/news_sponsors.html'),
        name='news_sponsors'),

    url(r'^news_speakers.html$',
        TemplateView.as_view(template_name='pycon/news_speakers.html'),
        name='news_speakers'),

    url(r'^news_recordings.html$',
        TemplateView.as_view(template_name='pycon/news_recordings.html'),
        name='news_recordings'),

    url(r'^news_lightning.html$',
        TemplateView.as_view(template_name='pycon/news_lightning.html'),
        name='news_lightning'),

    url(r'^news_spaces.html$',
        TemplateView.as_view(template_name='pycon/news_spaces.html'),
        name='news_spaces'),

    url(r'^speakers.html$',
        generic_views.ListView.as_view(
            queryset=models.SpeakerRegistration.objects.filter(approved=True),
            template_name='pycon/speakers.html'),
        name='speakers'),

    url(r'^speaker/(?P<pk>\d+)/detail.html$',
        generic_views.DetailView.as_view(
            queryset=models.SpeakerRegistration.objects.filter(approved=True),
            template_name='pycon/speaker_detail.html'),
        name='speaker_detail'),

)
