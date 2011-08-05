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

from zope import component

import unittest
from cStringIO import StringIO

from zope.configuration.xmlconfig import xmlconfig, XMLConfig
from zope.testing.doctestunit import DocTestSuite
from zope.app.testing.placelesssetup import PlacelessSetup

import z3c.zalchemy
from z3c.zalchemy.interfaces import IAlchemyEngineUtility

template = """<configure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:test='http://www.zope.org/NS/Zope3/test'
   xmlns:alchemy='http://namespaces.zalchemy.org/alchemy'
   i18n_domain='zope'>
   %s
   </configure>"""

class TestDirectives(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(TestDirectives, self).setUp()
        XMLConfig('meta.zcml', z3c.zalchemy)()

    def testDefaultEngineDirective(self):
        xmlconfig(StringIO(template % (
            '''
            <alchemy:engine
                url="sqlite://testdatabase.db"
                echo="True"
                />
            '''
            )))
        util = component.getUtility(IAlchemyEngineUtility)
        self.assertNotEqual(util, None)
        self.assertEqual(util.dsn, 'sqlite://testdatabase.db')
        self.assertEqual(util.echo, True)

    def testEngineDirective(self):
        xmlconfig(StringIO(template % (
            '''
            <alchemy:engine
                name="sqlite"
                url="sqlite://testdatabase.db"
                echo="True"
                />
            '''
            )))
        util = component.getUtility(IAlchemyEngineUtility,'sqlite')
        self.assertNotEqual(util, None)
        self.assertEqual(util.dsn, 'sqlite://testdatabase.db')
        self.assertEqual(util.echo, True)

    def testConnectDirective(self):
        from environ import testTable, mappedTestClass
        xmlconfig(StringIO(template % (
            '''
            <alchemy:engine
                name="sqlite-in-memory"
                url="sqlite://:memory:"
                />
            <alchemy:connectTable
                table="testTable"
                engine="sqlite-in-memory"
                />
            <alchemy:connectClass
                class="z3c.zalchemy.tests.environ.mappedTestClass"
                engine="sqlite-in-memory"
                />
            '''
            )))
        util = component.getUtility(IAlchemyEngineUtility, 'sqlite-in-memory')
        self.assert_(len(z3c.zalchemy.datamanager._tableToEngine)==1)
        self.assert_('testTable' in z3c.zalchemy.datamanager._tableToEngine)
        self.assert_(mappedTestClass in z3c.zalchemy.datamanager._classToEngine)

    def tearDown(self):
        z3c.zalchemy.datamanager._tableToEngine.clear()
        z3c.zalchemy.datamanager._classToEngine.clear()
        PlacelessSetup.tearDown(self)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestDirectives),
        ))

if __name__ == "__main__":
    unittest.TextTestRunner().run(test_suite())

