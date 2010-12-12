# -*- coding: utf-8 -*-
###############################################################################
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
###############################################################################
"""RML-to-PDF View

$Id: rml.py 80023 2007-09-25 16:17:12Z dominikhuber $
"""
__docformat__ = "reStructuredText"

import cStringIO
from zope.publisher.browser import BrowserPage
from z3c.rml import rml2pdf

class RML2PDFView(BrowserPage):

    template = None
    encoding = u'iso-8859-1'

    def __call__(self):
        rml = self.template(self).encode(self.encoding)
        self.request.response.setHeader('content-type', 'application/pdf')
        return rml2pdf.parseString(rml).read()
