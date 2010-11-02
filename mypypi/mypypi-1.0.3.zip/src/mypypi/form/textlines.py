##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH and Contributors.
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
$Id: textlines.py 1375 2009-05-12 22:07:03Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface

from z3c.form import interfaces
from z3c.form import widget
from z3c.form.browser import textarea
from mypypi.form.interfaces import ITextLinesWidget


class TextLinesWidget(textarea.TextAreaWidget):
    """Input type sequence widget implementation."""
    zope.interface.implementsOnly(ITextLinesWidget)


def TextLinesFieldWidget(field, request):
    """IFieldWidget factory for TextLinesWidget."""
    return widget.FieldWidget(field, TextLinesWidget(request))


@zope.interface.implementer(interfaces.IFieldWidget)
def TextLinesFieldWidgetFactory(field, value_type, request):
    """IFieldWidget factory for TextLinesWidget."""
    return TextLinesFieldWidget(field, request)
