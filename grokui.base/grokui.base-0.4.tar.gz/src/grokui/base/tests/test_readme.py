# -*- coding: utf-8 -*-

import unittest, doctest
import grokui.base
from zope.app.wsgi.testlayer import BrowserLayer


def test_suite():
    suite = unittest.TestSuite()
    readme = doctest.DocFileSuite(
        '../README.txt',
        optionflags=(doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE|
                     doctest.REPORT_NDIFF))
    readme.layer = BrowserLayer(grokui.base)
    suite.addTest(readme)
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
