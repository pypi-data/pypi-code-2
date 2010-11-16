##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Optional Dropdown Widget Tests"""

import doctest
import unittest
from zope.app.testing import placelesssetup
from pprint import pprint


def test_suite():
    return doctest.DocFileSuite(
        'README.txt',
        setUp=placelesssetup.setUp, tearDown=placelesssetup.tearDown,
        globs={'pprint': pprint},
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
