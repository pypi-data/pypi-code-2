##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""REST Tests"""

from z3c.rest import interfaces
from zope.app.testing import functional, placelesssetup
from zope.testing import renormalizing
from zope.traversing.browser import absoluteurl
from zope.traversing.interfaces import IContainmentRoot
import doctest
import os
import pprint
import re
import unittest
import zope.component
import zope.traversing.testing


RESTLayer = functional.ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'RESTLayer', allow_teardown=True)


def compatible_pprint(dict):
    """Compatible output for Python 2.4 till 2.6."""
    return pprint.pprint(dict, width=1)


def setUp(test):
    placelesssetup.setUp(test)
    zope.traversing.testing.setUp()

    # XXX: This really needs a REST equivalent w/o breadcrumbs.

    zope.component.provideAdapter(
        absoluteurl.AbsoluteURL,
        (None, interfaces.IRESTRequest),
        absoluteurl.IAbsoluteURL)

    zope.component.provideAdapter(
        absoluteurl.SiteAbsoluteURL,
        (IContainmentRoot, interfaces.IRESTRequest),
        absoluteurl.IAbsoluteURL,
        'absolute_url')

    zope.component.provideAdapter(
        absoluteurl.SiteAbsoluteURL,
        (IContainmentRoot, interfaces.IRESTRequest),
        absoluteurl.IAbsoluteURL)

    zope.component.provideAdapter(
        absoluteurl.AbsoluteURL,
        (None, interfaces.IRESTRequest),
        absoluteurl.IAbsoluteURL,
        'absolute_url')


def test_suite():
    client = functional.FunctionalDocFileSuite(
        '../client.txt',
        checker=renormalizing.RENormalizing([
            (re.compile('\[Errno 61\] Connection refused'),
             "(61, 'Connection refused')")
            ]))
    client.layer = RESTLayer
    return unittest.TestSuite((
        client,
        doctest.DocFileSuite(
            '../rest.txt',
            globs={'pprint': compatible_pprint},
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        doctest.DocFileSuite(
            '../error.txt',
            setUp=setUp, tearDown=placelesssetup.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        doctest.DocFileSuite(
            '../null.txt',
            setUp=setUp, tearDown=placelesssetup.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        doctest.DocFileSuite(
            '../traverser.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        ))
