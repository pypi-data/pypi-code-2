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
"""PML-to-PDF View

$Id: pml.py 73066 2007-03-08 15:44:06Z srichter $
"""
__docformat__ = "reStructuredText"

import xml.dom.minidom
from StringIO import StringIO

from zope.publisher.browser import BrowserPage

from z3c.pdftemplate.pml2pdf.Parser import TemplateParser, DocumentParser
from z3c.pdftemplate.pdf import PDFTemplateGenerator, ResourceHandler

class PML2PDFView(PDFTemplateGenerator, BrowserPage):

    document = None

    def __call__(self):
        # create the PDFDocment from xml
        document_xml = self.document(self).encode('utf-8')
        document_dom = xml.dom.minidom.parseString(document_xml)
        document = DocumentParser(document_dom, 'utf-8', ResourceHandler())

        # create the PDF itself using the document and the template
        buffer = StringIO()
        document(self.getPDFTemplate(), buffer)
        buffer.seek(0)

        # Set the content type to application/pdf
        self.request.response.setHeader('content-type', 'application/pdf')

        return buffer.read()
