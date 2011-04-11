##############################################################################
#
# Copyright (c) 2011 Zope Foundation and Contributors.
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
from fanstatic import Library, Resource
from fanstatic import get_needed

foo = Library("foo", "foo_dir")

a = Resource(foo, "a.js")

b = Resource(foo, "b.js", depends=[a])

class TestSingle(object):
    def widget(self):
        a.need()
        return "the widget HTML itself"

class TestMultiple(object):
    def widget(self):
        b.need()
        return "the widget HTML itself"

class TestBottom(object):
    def widget(self):
        b.need()
        # XXX this does not use any official API and needs to be
        # reconsidered. Its done anyway now to make the tests pass,
        # instead of just removing the corresponding test.
        get_needed()._bottom = True
        get_needed()._force_bottom = True
        return "the widget HTML itself"

class TestInlineResource(object):
    pass

class TestError(object):
    def widget(self):
        b.need()
        raise Exception('I am not a teapot')

