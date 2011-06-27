# Copyright (C) 2010, 2011 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of lava-dev-tool
#
# lava-dev-tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# lava-dev-tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lava-dev-tool.  If not, see <http://www.gnu.org/licenses/>.

import doctest
import unittest


def app_modules():
    return [
        'lava_dev_tool.document',
    ]


def test_modules():
    return [
        'lava_dev_tool.tests.test_document',
        'lava_dev_tool.tests.test_component',
        'lava_dev_tool.tests.test_project',
    ]


def test_suite():
    """
    Build an unittest.TestSuite() object with all the tests in _modules.
    Each module is harvested for both regular unittests and doctests
    """
    modules = app_modules() + test_modules()
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for name in modules:
        try:
            __import__(name, fromlist=[''])
        except ImportError:
            raise
        unit_suite = loader.loadTestsFromName(name)
        suite.addTests(unit_suite)
        try:
            doc_suite = doctest.DocTestSuite(name)
        except ValueError:
            # No doctests, ignore it!
            pass
        else:
            suite.addTests(doc_suite)
    return suite
