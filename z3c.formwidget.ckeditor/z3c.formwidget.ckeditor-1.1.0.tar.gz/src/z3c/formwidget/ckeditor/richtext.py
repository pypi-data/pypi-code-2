##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""RichText Field implementation

$Id: richtext.py 105467 2009-11-03 21:56:22Z srichter $
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.schema
from z3c.formwidget.ckeditor import interfaces

class RichText(zope.schema.Text):
    zope.interface.implements(interfaces.IRichText)
