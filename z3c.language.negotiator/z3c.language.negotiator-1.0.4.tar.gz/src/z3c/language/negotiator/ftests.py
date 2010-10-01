##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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

"""
$Id: ftests.py 71125 2006-11-15 04:43:00Z rogerineichen $
"""

import unittest

from zope.testing import doctest
from zope.app.testing import functional


def test_suite():
    return unittest.TestSuite((
        functional.FunctionalDocFileSuite(
            "browser.txt",
            optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')