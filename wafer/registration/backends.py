from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db import IntegrityError

from wafer.users.models import UserProfile


class GitHubBackend(ModelBackend):

    def authenticate(self, github_login, name, email, blog):
        if not github_login:
            return
        try:
            return UserProfile.objects.get(github_username=github_login).user
        except UserProfile.DoesNotExist:
            return self._create_user(github_login, name, email, blog)

    def _create_user(self, github_login, name, email, blog, append=0):
        try:
            user = User.objects.create(username=(github_login + str(append)
                                                 if append else github_login))
        except IntegrityError:
            return self._create_user(github_login, name, email, blog,
                                     append + 1)

        user.first_name, _,  user.last_name = name.partition(' ')
        user.email = email
        user.save()

        profile = user.get_profile()
        profile.homepage = blog
        profile.github_username = github_login
        profile.save()

        return user
