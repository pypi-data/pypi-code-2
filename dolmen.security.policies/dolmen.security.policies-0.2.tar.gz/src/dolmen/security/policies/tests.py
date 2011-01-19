# -*- coding: utf-8 -*-

import doctest
import unittest
import pprint
import dolmen.security.policies
from zope.component.testlayer import ZCMLFileLayer

layer = ZCMLFileLayer(dolmen.security.policies)


def test_suite():
    suite = unittest.TestSuite()
    files = ('README.txt',)
    for filename in files:
        docfile = doctest.DocFileSuite(
            filename,
            globs={'pprint': pprint.pprint},
            optionflags=(doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS))
        docfile.layer = layer
        suite.addTest(docfile)
    return suite
