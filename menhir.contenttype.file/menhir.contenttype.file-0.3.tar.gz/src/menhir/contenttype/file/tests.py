# -*- coding: utf-8 -*-

import doctest
import unittest
import menhir.contenttype.file
from zope.component.testlayer import ZCMLFileLayer


def test_suite():
    suite = unittest.TestSuite()
    readme = doctest.DocFileSuite(
        'README.txt',
        globs={"__name__": "menhir.contenttype.file"},
        optionflags=(doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS))
    readme.layer = ZCMLFileLayer(menhir.contenttype.file)
    suite.addTest(readme)
    return suite
