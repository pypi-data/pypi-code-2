# -*- coding: utf-8 -*-

import grokcore.component as grok
from dolmen.file import INamedFile
from zope.size import byteDisplay
from zope.size.interfaces import ISized


class Sized(grok.Adapter):
    grok.context(INamedFile)
    grok.implements(ISized)

    def sizeForSorting(self):
        return "byte", self.context.size

    def sizeForDisplay(self):
        return byteDisplay(self.context.size)
