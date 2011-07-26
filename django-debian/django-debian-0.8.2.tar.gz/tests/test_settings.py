# Copyright (C) 2011 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of django-debian.
#
# django-debian is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# django-debian is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with django-debian.  If not, see <http://www.gnu.org/licenses/>.

"""
Tests for Settings class
"""

from unittest import TestCase
from fs_mock import MockedFileSystem

from django_debian.settings import Settings


class SettingsDefaultsTests(TestCase):

    def setUp(self):
        fs = MockedFileSystem()
        with fs.replay():
            # Replay in isolation mode acts as an empty filesystem
            # this is exactly what we want to observe.
            self.settings = Settings('test')

    def test_DEBUG(self):
        self.assertEqual(self.settings.DEBUG, False)

    def test_MEDIA_ROOT(self):
        self.assertEqual(self.settings.MEDIA_ROOT, "/var/lib/test/media/")

    def test_MEDIA_URL(self):
        self.assertEqual(self.settings.MEDIA_URL, "/test/media/")

    def test_STATIC_ROOT(self):
        self.assertEqual(self.settings.STATIC_ROOT, "/var/lib/test/static/")

    def test_STATIC_URL(self):
        self.assertEqual(self.settings.STATIC_URL, "/test/static/")

    def test_ADMIN_MEDIA_PREFIX(self):
        self.assertEqual(self.settings.ADMIN_MEDIA_PREFIX, "/test/static/admin/")

    def test_TEMPLATE_DIRS(self):
        self.assertEqual(self.settings.TEMPLATE_DIRS, (
            "/etc/test/templates/", "/usr/share/test/templates/"))

    def test_STATICFILES_DIRS(self):
        self.assertEqual(self.settings.STATICFILES_DIRS, (
            ("test", "/usr/share/test/htdocs/"),))

    def test_ADMINS(self):
        self.assertEqual(self.settings.ADMINS, (
            ("test Administrator", 'root@localhost'),))

    def test_MANAGERS(self):
        self.assertEqual(self.settings.ADMINS, (
            ("test Administrator", 'root@localhost'),))

    def test_SEND_BROKEN_LINK_EMAILS(self):
        self.assertEqual(self.settings.SEND_BROKEN_LINK_EMAILS, False)
