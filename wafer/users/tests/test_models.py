# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
"""Tests for wafer.user.models"""

from django.test import TestCase
from wafer.tests.utils import create_user


class UserModelTestCase(TestCase):

    def test_str_method_issue192(self):
        """Test that str(user) works correctly"""
        user = create_user('test')
        self.assertEqual(str(user.userprofile), 'test')
