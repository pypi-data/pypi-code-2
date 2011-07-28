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
Package with unit tests for django-debian
"""

import doctest
import unittest

TEST_MODULES = [
    'django_debian.config_file',
    'django_debian.dbconfig',
    'django_debian.secret_key',
    'django_debian.settings',
    'tests.test_config_file',
    'tests.test_fs_mock',
    'tests.test_settings',
]


def suite(modules=None):
    """
    Build an unittest.TestSuite() object with all the tests in _modules.
    Each module is harvested for both regular unittests and doctests
    """
    if modules is None:
        modules = TEST_MODULES
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for module_name in modules:
        try:
            module = __import__(module_name, fromlist=[''])
        except ImportError:
            import logging
            logging.exception("Unable to import test module %s", module_name)
            raise
        unit_suite = loader.loadTestsFromName(module_name)
        suite.addTests(unit_suite)
        doc_suite = doctest.DocTestSuite(module_name)
        suite.addTests(doc_suite)
    return suite
