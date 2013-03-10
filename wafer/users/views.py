from django.contrib.auth.models import User
from django.views.generic import DetailView


class ProfileView(DetailView):
    template_name = 'wafer.users/profile.html'
    queryset = User.objects.all()
    slug_field = 'username'
    slug_url_kwarg = 'username'
