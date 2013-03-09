from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404

from wafer.models import SpeakerRegistration


def attendee_talk(request, speaker_name):
    """Display the submitted talks associated with the given user"""
    speaker = get_object_or_404(SpeakerRegistration, name=speak_nam)
    if speaker.talk_title is None:
        return HttpResponseNotFound("Talk details not found.",
                                    content_type="text/plain")


    return HttpResponse(
            content="<html><body>Talks still to be done</body></html>",
            content_type="text/html")
