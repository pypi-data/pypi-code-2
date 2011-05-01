##############################################################################
#
# Copyright (c) 2004-2006 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""
$Id: LayoutRegistry.py 238387 2011-04-30 19:58:15Z hathawsh $
"""

from Globals import PersistentMapping, Persistent

from ZODB.PersistentList import PersistentList

from Products.CompositePack.exceptions import CompositePackError

class LayoutsForType(Persistent):

    def __init__(self):
        self.viewlets = PersistentList()
        self.default = ''

    def append(self, item):
        if not item in self.viewlets:
            self.viewlets.append(item)

    def remove(self, item, force=False):
        if item == self.getDefault():
            if force:
                self.setDefault(None)
            else:
                msg = "Layout %s cannot be unregistered :" + \
                      " it is set as default."
                msg = msg % item
                raise CompositePackError, msg
        if item in self.viewlets:
            self.viewlets.remove(item)

    def getList(self):
        return self.viewlets

    def setDefault(self, item):
        if item in self.viewlets or item is None:
            self.default = item
        else:
            msg = "Layout %s cannot be set as default :" + \
                  " it is not registered."
            msg = msg % item
            raise CompositePackError, msg

    def getDefault(self):
        return self.default

class LayoutRegistry(PersistentMapping):

    def registerContentType(self, type):
        if not self.isContentTypeRegistered(type):
            self[type] = LayoutsForType()
        else:
            raise CompositePackError, '%s already registered' % type

    def unregisterContentType(self, type):
        if not self.isContentTypeRegistered(type):
            return
        del self[type]

    def getContentTypes(self):
        list = self.keys()
        list.sort()
        return list

    def isContentTypeRegistered(self, type):
        return self.has_key(type)

    def registerForType(self, layout_id, type):
        if not self.isContentTypeRegistered(type):
            self.registerContentType(type)
        self[type].append(layout_id)
        if not self.hasDefaultForType(type):
            self.setDefaultForType(layout_id, type)

    def unregisterForType(self, layout_id, type, force=False):
        if not self.isContentTypeRegistered(type):
            return
        self[type].remove(layout_id, force)

    def getForType(self, type, default=None):
        if not self.isContentTypeRegistered(type):
            return default
        return self[type].getList()

    def setDefaultForType(self, layout_id, type):
        if not self.isContentTypeRegistered(type):
            self.registerContentType(type)
        self[type].setDefault(layout_id)

    def getDefaultForType(self, type):
        if not self.isContentTypeRegistered(type):
            raise CompositePackError, "type %s not registered as composite" % type
        else:
            layout = self[type].getDefault()
            if layout:
                return layout
            else:
                raise CompositePackError, "no default layout registered for type %s" % type

    def hasDefaultForType(self, type):
        return self[type].getDefault() is not None

    def queryDefaultForType(self, type, default=None):
        if not self.isContentTypeRegistered(type):
            return default
        layout = self[type].getDefault()
        if layout:
            return layout
        return default
