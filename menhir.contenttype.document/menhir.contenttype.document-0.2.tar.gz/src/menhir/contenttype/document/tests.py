# -*- coding: utf-8 -*-

import doctest
import unittest
import menhir.contenttype.document
from zope.component.testlayer import ZCMLFileLayer


def test_suite():
    suite = unittest.TestSuite()
    readme = doctest.DocFileSuite(
        'README.txt',
        globs={"__name__": "menhir.contenttype.document"},
        optionflags=(doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS))
    readme.layer = ZCMLFileLayer(menhir.contenttype.document)
    suite.addTest(readme)
    return suite
