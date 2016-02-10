from rest_framework import serializers
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        # Arguably not useful to expose via the REST api without
        # more thought.
        exclude = ('password',)
