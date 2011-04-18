# -*- coding: utf-8 -*-
# $Id: controlpanel.py 237778 2011-04-18 10:40:52Z glenfant $
"""Our Zope 2 ZMI control panel"""

import Acquisition
from OFS import SimpleItem
from App.version_txt import getZopeVersion
from zope.interface import implements
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from zope.configuration.docutils import makeDocStructures
version = getZopeVersion()
if version > (2, 12):
    class Fake:
        pass
else:
    from App.ApplicationManager import Fake

from config import CONTROLPANEL_ID
from interfaces import IControlPanel

doc_namespaces = None
doc_subdirs = None

class ControlPanel(Fake, SimpleItem.Item, Acquisition.Implicit):
    """The Monkey patches control panel"""

    implements(IControlPanel)
    id = CONTROLPANEL_ID
    name = title = "ZCML Documentation"
    #manage_main = PageTemplateFile('zmi/controlpanel.pt', globals())

    manage_options=((
        {'label': 'ZCML documentation', 'action': 'manage_main'},
        ))

    def getId(self):
        """Required by ZMI
        """
        return self.id

    def getNamespaces(self):
        global doc_namespaces, doc_subdirs
        if doc_namespaces is None:
            from Products.Five.zcml import _context
            doc_namespaces, doc_subdirs = makeDocStructures(_context)
        return doc_namespaces

    def getSubdirs(self):
        global doc_namespaces, doc_subdirs
        if doc_subdirs is None:
            from Products.Five.zcml import _context
            doc_namespaces, doc_subdirs = makeDocStructures(_context)
        return doc_subdirs
