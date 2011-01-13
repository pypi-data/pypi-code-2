# -*- coding: utf-8 -*-

import doctest
import unittest
import dolmen.widget.tinymce
from zope.component.testlayer import ZCMLFileLayer


def test_suite():
    """Testing suite.
    """
    readme = doctest.DocFileSuite(
        'README.txt',
        optionflags=(doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE))
    readme.layer = ZCMLFileLayer(dolmen.widget.tinymce)
    suite = unittest.TestSuite()
    suite.addTest(readme)
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
