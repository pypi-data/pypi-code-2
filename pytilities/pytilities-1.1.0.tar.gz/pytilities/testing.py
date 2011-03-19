# Copyright (C) 2010 Tim Diels <limyreth@users.sourceforge.net>
# 
# This file is part of pytilities.
# 
# pytilities is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pytilities is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with pytilities.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Test utilities
"""

__docformat__ = 'reStructuredText'

import unittest
import os
import logging

_logger = logging.getLogger("pytilities.testing")

def get_recursive_package_test(root, test_package):
    """
    Get a test suite of all tests inside a package and its child packages

    Parameters:

        `root`:: string
            absolute path of the top package's directory of this python program

        `test_package`:: string
            name of package to search in for tests, in dotted format, e.g.
            'project.test'

    See the wiki for a usage example.

    Returns ::unittest.TestSuite
    """
    test_suite = unittest.TestSuite()

    for parent, dirs, files in os.walk(
            os.path.join(root, test_package.replace('.', os.path.sep))):

        if parent == '.svn' or '__init__.py' not in files:
            continue

        for file_ in files:
            if os.path.splitext(file_)[1] != '.py':
                continue

            file_path = os.path.join(parent[len(root)+1:],
                                     file_[:-3])

            module_full_name = file_path.replace(os.sep, '.')

            _logger.debug('Loading: %s' % module_full_name)

            test_suite.addTest(
                unittest.defaultTestLoader.loadTestsFromName(module_full_name))

    return test_suite

def run(test):
    """
    Run test and print results to stderr

    Parameters:

        `test`
            the TestCase to run
    """
    runner = unittest.TextTestRunner()
    return runner.run(test)
