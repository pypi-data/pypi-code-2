##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
"""
$Id: pagetemplate.py 74100 2007-04-11 08:15:17Z dobe $
"""
__docformat__ = "reStructuredText"

from zope import component

from zope.pagetemplate.interfaces import IPageTemplate

class RegisteredPageTemplate(object):

    def __call__(self, instance, *args, **keywords):
        template = component.getMultiAdapter(
                (instance, instance.request), IPageTemplate)
        return template(instance, *args, **keywords)

    def __get__(self, instance, type):
        return BoundRegisteredPageTemplate(self, instance)


class BoundRegisteredPageTemplate(object):
    def __init__(self, pt, ob):
        object.__setattr__(self, 'im_func', pt)
        object.__setattr__(self, 'im_self', ob)

    def __call__(self, *args, **kw):
        if self.im_self is None:
            im_self, args = args[0], args[1:]
        else:
            im_self = self.im_self
        return self.im_func(im_self, *args, **kw)

    def __setattr__(self, name, v):
        raise AttributeError("Can't set attribute", name)

    def __repr__(self):
        return "<BoundRegisteredPageTemplateFile of %r>" % self.im_self

