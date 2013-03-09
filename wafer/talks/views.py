from django.shortcuts import render
from django.http import HttpResponseRedirect

from wafer.talks.models import Talks
from wafer.talks.forms import SubmitTalkForm


def submit(request):
    """Submit a talk proposal"""
    if request.method == 'POST':
        form = SubmitTalkForm(request.POST)
        if form.is_valid():
            # FIXME
            return HttpResponseRedirect('/')
    else:
        form = SubmitTalkForm()

    return render(request, 'talks/submittalk.html', {
            'form': form,
            })
