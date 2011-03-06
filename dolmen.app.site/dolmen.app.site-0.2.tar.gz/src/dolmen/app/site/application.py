# -*- coding: utf-8 -*-

import grokcore.site
import dolmen.content
from zope.interface import Interface


class IDolmen(Interface):
    """This interface defines a Dolmen site root.
    """


class Dolmen(grokcore.site.Site, dolmen.content.Container):
    """A Dolmen Site Manager.
    """
    dolmen.content.nofactory()
    grokcore.site.implements(
        IDolmen, grokcore.site.interfaces.IApplication)
