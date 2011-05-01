##############################################################################
#
# Copyright (c) 2004-2006 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""
$Id: ViewletRegistry.py 238387 2011-04-30 19:58:15Z hathawsh $
"""

from Globals import PersistentMapping, Persistent
from ZODB.PersistentList import PersistentList

from Products.CompositePack.exceptions import CompositePackError

class ViewletsForType(Persistent):
    def __init__(self):
        self.viewlets  = PersistentList()
        self.default = ''
        self.use_default_viewlets = True
        self.use_default_default = True

    def append(self, item):
        if not item in self.viewlets:
            self.viewlets.append(item)
            self.use_default_viewlets = False

    def remove(self, item, force=False):
        if item == self.default:
            if force:
                self.setDefault(None)
            else:
                msg = "Viewlet %s cannot be unregistered :" + \
                      " it is set as default."
                msg = msg % item
                raise CompositePackError, msg
        if item in self.viewlets:
            self.viewlets.remove(item)
        if not self.viewlets:
            self.use_default_viewlets = True

    def getList(self):
        return self.viewlets

    def clearList(self):
        while self.viewlets:
            self.viewlets.pop()
        self.use_default_viewlets = True

    def setDefault(self, item):
        if self.use_default_viewlets or item in self.viewlets or item is None:
            self.default = item
            self.use_default_default = False
        else:
            msg = "Viewlet %s cannot be set as default :" + \
                  " it is not registered."
            msg = msg % item
            raise CompositePackError, msg

    def clearDefault(self):
        self.default = ''
        self.use_default_default = True

    def getDefault(self):
        return self.default

    def queryDefault(self, default=None):
        if self.default:
            return self.default
        else:
            return default

class DefaultViewletsForType(ViewletsForType):
    def __init__(self):
        self.has_default = False
        ViewletsForType.__init__(self)

    def getDefault(self):
        if self.has_default:
            return ViewletsForType.getDefault(self)
        else:    
            msg = 'Default viewlet not initialized for Default Setup'
            raise CompositePackError, msg 

    def queryDefault(self, default=None):
        if self.has_default:
            return ViewletsForType.queryDefault(self)
        else:
            return default

    def setDefault(self, item):
        ViewletsForType.setDefault(self, item)
        self.has_default = True

    def clearDefault(self, item):
        ViewletsForType.clearDefault(self)
        self.has_default = False

DEFAULT = '(Default Setup)'

class ViewletRegistry(PersistentMapping):

    def __init__(self):
        PersistentMapping.__init__(self)
        self[DEFAULT] = DefaultViewletsForType()

    def registerContentType(self, type):
        if not self.isContentTypeRegistered(type):
            self[type] = ViewletsForType()
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

    def registerForType(self, viewlet_id, type):
        if not self.isContentTypeRegistered(type):
            self.registerContentType(type)
        self[type].append(viewlet_id)
        if not self.hasDefaultForType(type):
            self.setDefaultForType(viewlet_id, type)

    def unregisterForType(self, viewlet_id, type, force=False):
        if not self.isContentTypeRegistered(type):
            return
        self[type].remove(viewlet_id, force)

    def getForType(self, type):
        if (not self.isContentTypeRegistered(type) or
            self[type].use_default_viewlets):
            return self[DEFAULT].getList()
        else:
            return self[type].getList()

    def hasDefaultForType(self, type):
        return self[type].queryDefault() is not None

    def setDefaultForType(self, viewlet_id, type):
        if not self.isContentTypeRegistered(type):
            self.registerContentType(type)
        self[type].setDefault(viewlet_id)

    def getDefaultForType(self, type):
        if (not self.isContentTypeRegistered(type) or
            self[type].use_default_default):
            return self[DEFAULT].getDefault()
        else:
            default = self[type].getDefault()
            if default:
                if self[type].use_default_viewlets and default not in self[DEFAULT].getList():
                    msg = "Default viewlet (%s) registered for type %s "
                    msg += "is no more registered in default setup viewlets."
                    msg = msg % (default, type)
                    raise CompositePackError, msg
                return default
            else:
                msg = "No default viewlet registered for %s" % type
                raise CompositePackError, msg

    def setTypeUseDefaultSetup(self, type):
        if not self.isContentTypeRegistered(type):
            self.registerContentType(type)
        self[type].clearList()

    def getTypeUseDefaultSetup(self, type):
        return self[type].use_default_viewlets

    def clearForType(self, type):
        self.setTypeUseDefaultSetup(type)

    def setTypeUseDefaultFromDefaultSetup(self, type):
        if not self.isContentTypeRegistered(type):
            self.registerContentType(type)
        self[type].clearDefault()

    def getTypeUseDefaultFromDefaultSetup(self, type):
        return self[type].use_default_default

