##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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

from zope.testing import doctest, renormalizing
import gocept.zeoraid.scripts.controller
import re
import unittest
import zc.buildout.testing


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('gocept.zeoraid', test)
    zc.buildout.testing.install('mock', test)
    zc.buildout.testing.install('zc.lockfile', test)
    zc.buildout.testing.install('zc.zodbrecipes', test)
    zc.buildout.testing.install('zope.event', test)
    zc.buildout.testing.install('zope.testing', test)
    zc.buildout.testing.install('zc.recipe.egg', test)
    zc.buildout.testing.install('zope.exceptions', test)
    zc.buildout.testing.install('zdaemon', test)
    zc.buildout.testing.install('ZConfig', test)
    zc.buildout.testing.install('ZODB3', test)
    zc.buildout.testing.install('transaction', test)
    zc.buildout.testing.install('zope.proxy', test)
    zc.buildout.testing.install('zope.interface', test)


checker = renormalizing.RENormalizing([
    zc.buildout.testing.normalize_path,
    (re.compile(
    "Couldn't find index page for '[a-zA-Z0-9.]+' "
    "\(maybe misspelled\?\)"
    "\n"), ''),
    (re.compile('#![^\n]+\n'), ''),
    (re.compile('-\S+-py\d[.]\d(-\S+)?.egg'),
     '-pyN.N.egg',
    ),
    ])


class TestController(unittest.TestCase):

    def test_disconnected_fails(self):
        self.assertRaises(RuntimeError,
            gocept.zeoraid.scripts.controller.RAIDManager,
            '127.0.0.10', '4000', '1')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
            'recipe.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            checker=checker,
            optionflags=doctest.REPORT_NDIFF | doctest.ELLIPSIS))
    suite.addTest(unittest.makeSuite(TestController))
    return suite
