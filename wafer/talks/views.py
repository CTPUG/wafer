from django.shortcuts import render
from django.http import HttpResponseRedirect

from wafer.talks.models import Talks
from wafer.talks.forms import SubmitTalkForm


def submit(request):
    """Submit a talk proposal"""
    if request.method == 'POST':
        form = SubmitTalkForm(request.POST)
        if form.is_valid():
            if not request.user.is_authenticated():
                # Shouldn't happen, but let's be paranoid
                return HttpResponseRedirect('/')
            title = form.cleaned_data['title']
            abstract = form.cleaned_data['abstract']
            user = request.user
            # FIXME: Valid that all the authors exist in the
            # database
            talk = Talks.objects.create(title=title,
                    abstract=abstract, corresponding_author=user)
            return HttpResponseRedirect('/')
    else:
        form = SubmitTalkForm()

    return render(request, 'talks/submittalk.html', {
            'form': form,
            })
