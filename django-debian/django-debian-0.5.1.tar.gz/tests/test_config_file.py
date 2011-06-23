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
Test suite for the package
"""

from unittest import TestCase

from django_debian.config_file import ConfigFile
from fs_mock import MockedFileSystem


class TestConfigFile(TestCase):

    _CONFIG_FILE_NAME = "config.conf"

    def mocked_config_file(self, contents):
        fs = MockedFileSystem()
        with fs.record():
            with open(self._CONFIG_FILE_NAME, "wt") as stream:
                stream.write(contents)
        with fs.replay():
            return ConfigFile.load(self._CONFIG_FILE_NAME)

    def test_load(self):
        data = self.mocked_config_file(
            "value1='foo'\n"
            "value2='bar'\n")
        self.assertEqual(data.value1, "foo")
        self.assertEqual(data.value2, "bar")
