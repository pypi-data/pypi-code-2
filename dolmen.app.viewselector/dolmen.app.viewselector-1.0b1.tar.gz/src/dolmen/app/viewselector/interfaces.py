#!/usr/bin/python
# -*- coding: utf-8 -*-

from zope.schema import TextLine
from zope.interface import Interface
from dolmen.app.viewselector import MF as _


class IViewSelector(Interface):
    """A component aware of dynamic views.
    """
    selected_view = TextLine(
        title=_(u"Selected View"),
        default=u"base_view",
        required=True,
        )
