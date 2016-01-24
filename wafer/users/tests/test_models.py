# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8 ai ts=4 sts=4 et sw=4
"""Tests for wafer.user.models"""

from django.contrib.auth import get_user_model
from django.test import TestCase

import sys
PY2 = sys.version_info[0] == 2


class UserModelTestCase(TestCase):

    def test_str_method_issue192(self):
        """Test that str(user) works correctly"""
        create = get_user_model().objects.create_user
        user = create('test', 'test@example.com', 'test_pass')
        self.assertEqual(str(user.userprofile), 'test')
        user = create(u'tést', 'test@example.com', 'test_pass')
        if PY2:
            self.assertEqual(unicode(user.userprofile), u'tést')
        else:
            self.assertEqual(str(user.userprofile), u'tést')
