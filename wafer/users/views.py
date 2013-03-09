from django.contrib.auth.models import User
from django.http import Http404
from django.views.generic import TemplateView


class ProfileView(TemplateView):
    template_name = 'wafer.users/profile.html'

    def get_context_data(self, username):
        try:
            subject = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404
        return {
            'subject': subject,
            'profile': subject.get_profile(),
        }
