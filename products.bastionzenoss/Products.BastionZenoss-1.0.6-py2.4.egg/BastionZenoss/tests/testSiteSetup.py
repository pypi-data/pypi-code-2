#
#    Copyright (C) 2010  Corporation of Balclutha. All rights Reserved.
#
#                All Rights Reserved
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
#
# Corporation of Balclutha DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS, IN NO EVENT SHALL Corporation of Balclutha BE LIABLE FOR
# ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE. 
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc

ztc.installProduct('Five')
ztc.installProduct('BastionZenoss')


ptc.setupPloneSite(products=['BastionZenoss'])


class TestSetup(ptc.PloneTestCase):
    """
    Testing with Plone install and Plone skins ...
    """

    def testZentinel(self):
        self.failUnless('zport' in self.app.objectIds())

    def testPlone(self):
        self.failUnless('plone' in self.app.objectIds())

        plone = self.app.plone
        self.failUnless('zentinel' in plone.objectIds())
        self.failUnless('zenreports' in plone.objectIds())

if __name__ == '__main__':
    framework()
else:
    def test_suite():
        from unittest import TestSuite, makeSuite
        suite = TestSuite()
        suite.addTest(makeSuite(TestSetup))
        return suite
