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
"""Directive Handler for several PDF generating presentation components

$Id: zcml.py 80023 2007-09-25 16:17:12Z dominikhuber $
"""
__docformat__ = "reStructuredText"

import os.path

from zope.configuration.exceptions import ConfigurationError
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema import TextLine

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.publisher.browser.metadirectives import IPageDirective
from zope.app.publisher.browser.viewmeta import page

from z3c.pdftemplate.rml import RML2PDFView


class IRMLToPDFDirective(IPageDirective):
    """A view directive that dynamically evaluates a RML document and converts
    it to PDF.

    This directive behaves very much like the ``page`` directive, except that
    it does not generate HTML, but RML that is rendered to PDF for output. RML
    is a simple XML-dialect that creates a storyboard for the reportlab PDF
    rendering engine.
    """

    encoding = TextLine(
        title=u'Encoding',
        description=u'Encoding of the template.',
        required=False,
        default=u'iso-8859-1',
        )


def rml2pdf(_context, name, permission, for_, template,
            layer=IDefaultBrowserLayer, class_=RML2PDFView,
            allowed_interface=None, allowed_attributes=None,
            menu=None, title=None, encoding=u'iso-8859-1'):

    if class_ is not RML2PDFView and RML2PDFView not in class_.__bases__:
        bases = (class_, RML2PDFView)
    else:
        bases = (class_,)

    factory = type(
        'RML2PDFView from template=%s' %(str(template)),
        bases,
        {'template': ViewPageTemplateFile(template),
         'encoding': encoding}
        )

    page(_context, name, permission, for_, layer, None, factory,
         allowed_interface, allowed_attributes, '__call__', menu, title)
