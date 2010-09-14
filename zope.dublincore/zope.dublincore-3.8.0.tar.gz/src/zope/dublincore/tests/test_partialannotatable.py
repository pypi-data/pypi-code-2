"""Tests of the 'partial' annotatable adapter.

"""
__docformat__ = "reStructuredText"

import doctest
import zope.component.testing
from zope.component.testing import tearDown
from zope.annotation.attribute import AttributeAnnotations

def setUp(test):
    zope.component.testing.setUp(test)
    zope.component.provideAdapter(AttributeAnnotations)

def test_suite():
    return doctest.DocFileSuite(
        "partial.txt", setUp=setUp, tearDown=tearDown)
