##############################################################################
#
# Copyright (c) 2006 ROBOTECH Logistiksysteme GmbH and Contributors.
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
import os
import unittest
import doctest
from zope.app.testing import setup
from zope.testing.doctestunit import DocFileSuite
from zope.app.testing.placelesssetup import PlacelessSetup

import z3c.zalchemy


def setUp(test):
    setup.placefulSetUp()
    z3c.zalchemy.testing.setUp(test)
    test.globs['dbTrFilename'] = 'z3c.zalchemy.test.transaction.db'
    test.globs['dbFilename'] = 'z3c.zalchemy.test1.db'
    test.globs['dbFilename2'] = 'z3c.zalchemy.test2.db'

def tearDown(test):
    z3c.zalchemy.testing.tearDown(test)
    try:
        os.remove(test.globs['dbTrFilename'])
    except:
        pass
    try:
        os.remove(test.globs['dbFilename'])
    except:
        pass
    try:
        os.remove(test.globs['dbFilename2'])
    except:
        pass
    setup.placefulTearDown()


class TestDefaultEngine(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(TestDefaultEngine, self).setUp()
        z3c.zalchemy.testing.setUp(self)

    def tearDown(self):
        super(TestDefaultEngine, self).tearDown()
        z3c.zalchemy.testing.tearDown(self)

    def testNoDefaultEngine(self):
        # Our session can't work without an engine. If we did not 
        # register an IAlchemyEngineUtility, we can't access the session
        self.assertRaises(ValueError, z3c.zalchemy.getSession)

    def testDefaultEngine(self):
        from zope.component import provideUtility
        from z3c.zalchemy.interfaces import IAlchemyEngineUtility
        from z3c.zalchemy.datamanager import AlchemyEngineUtility
        engineUtility = z3c.zalchemy.datamanager.AlchemyEngineUtility(
                'database',
                'sqlite:///:memory:')
        provideUtility(engineUtility, IAlchemyEngineUtility)
        session = z3c.zalchemy.getSession()
        self.assertNotEqual(session, None)
        self.assertNotEqual(session.get_bind(None), None)

    def testResetEngine(self):
        engineUtility = z3c.zalchemy.datamanager.AlchemyEngineUtility(
                'database',
                'sqlite:///:memory:')
        engine = engineUtility.getEngine()
        self.assertEquals(engine, engineUtility._v_engine)
        engineUtility._resetEngine()
        self.assert_(engineUtility._v_engine is None)


def test_suite():
    return unittest.TestSuite((
        DocFileSuite('TRANSACTION.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        unittest.makeSuite(TestDefaultEngine),
        DocFileSuite('../README.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

