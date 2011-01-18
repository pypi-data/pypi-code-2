# -*- coding: utf-8 -*-

import unittest
import doctest
import fanstatic
import megrok.resourceviewlet.ftests
from zope.fanstatic.testing import ZopeFanstaticBrowserLayer


class TestLayer(ZopeFanstaticBrowserLayer):
    def setup_middleware(self, app):
        return fanstatic.Injector(app)

layer = TestLayer(megrok.resourceviewlet.ftests)

def test_suite():
    readme = doctest.DocFileSuite(
        '../README.txt',
        globs={'__name__': 'megrok.resourceviewlet.ftests'},
        optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)
    readme.layer = layer
    return unittest.TestSuite([readme])
