##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import doctest
import unittest
from zope.testing import setupstack

def test_suite():
    return doctest.DocFileSuite(
        'sbo.test',
        optionflags=doctest.NORMALIZE_WHITESPACE,
        setUp=setupstack.setUpDirectory, tearDown=setupstack.tearDown,
        )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
