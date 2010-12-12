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
"""PDF Template Package
$Id: __init__.py 73066 2007-03-08 15:44:06Z srichter $
"""
__docformat__ = "reStructuredText"

from reportlab.pdfbase import pdfmetrics

# Register some initial fonts.
pdfmetrics.registerFont(pdfmetrics.Font('Helvetica-WinAnsi',
                                        'Helvetica',
                                        'WinAnsiEncoding'))
pdfmetrics.registerFont(pdfmetrics.Font('Helvetica-Bold-WinAnsi',
                                        'Helvetica-Bold',
                                        'WinAnsiEncoding'))
pdfmetrics.registerFont(pdfmetrics.Font('Helvetica-BoldOblique-WinAnsi',
                                        'Helvetica-BoldOblique',
                                        'WinAnsiEncoding'))
