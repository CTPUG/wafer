"""Tests for wafer.user.models"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from wafer.users.models import create_user_profile



class UserModelTestCase(TestCase):

    def test_str_method_issue192(self):
        """Test that str(user) works correctly"""
        create = get_user_model().objects.create_user
        user = create('test', 'test@example.com', 'test_pass')
        self.assertEqual(str(user.userprofile), 'test')
