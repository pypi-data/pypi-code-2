##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""REST publication and publisher factories

$Id: error.py 82249 2007-12-11 00:07:36Z srichter $
"""
import zope.component
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from z3c.rest import rest


class XMLErrorView(rest.RESTView):

    template = ViewPageTemplateFile('error.pt')

    def update(self):
        self.name = self.context.__class__.__name__
        self.explanation = unicode(str(self.context))

    def __call__(self):
        self.update()
        return self.template()
