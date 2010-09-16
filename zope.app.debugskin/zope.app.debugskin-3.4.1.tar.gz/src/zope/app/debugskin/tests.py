##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
""" Unit tests for the 'exceptions' view.

$Id: tests.py 81390 2007-11-01 21:38:36Z srichter $
"""
__docformat__ = 'restructuredtext'
import unittest
from zope.app.debugskin.exceptions import ExceptionDebugView
from zope.app.debugskin.testing import DebugSkinLayer
from zope.app.testing.functional import BrowserTestCase

class TestExceptions(unittest.TestCase):

    def _getTargetClass(self):
        return ExceptionDebugView

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_tracebackLines(self):
        import sys
        import traceback
        try:
            1/0
        except:
            context = sys.exc_info()[0]
            request = None
            view = self._makeOne(context, request)
            self.assertEqual(view.error_type, sys.exc_info()[0])
            self.assertEqual(view.error_object, sys.exc_info()[1])
            tb_lines = traceback.extract_tb(sys.exc_info()[2])
            self.assertEqual(len(view.traceback_lines), len(tb_lines))


class DebugSkinTests(BrowserTestCase):

    def testNotFound(self):
        response = self.publish('/++skin++Debug/foo',
                                basic='mgr:mgrpw', handle_errors=True)
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(body.find(
            'zope.publisher.interfaces.NotFound') > 0)
        self.assert_(body.find(
            'in publishTraverse') > 0)
        self.checkForBrokenLinks(body, '/++skin++Debug/foo',
                                 basic='mgr:mgrpw')


def test_suite():
    DebugSkinTests.layer = DebugSkinLayer
    return unittest.TestSuite((
        unittest.makeSuite(TestExceptions),
        unittest.makeSuite(DebugSkinTests),
        ))

