##############################################################################
#
# Copyright (c) 2004-2006 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""
$Id: CPpermissions.py 11303 2005-08-23 16:38:33Z godchap $
"""

from StringIO import StringIO
from zLOG import INFO, ERROR

from Products.CMFPlone.setup.SetupBase import SetupWidget

def cleanIndexes(self, portal):
    catalog = portal.portal_catalog
    TYPES_TO_CLEAN = ['CompositePack Layout Container',
                      'CompositePack Viewlet Container',
                      'CompositePack Viewlet',
                      'CompositePack Layout',
                      'Pack Composite',
                     ]
    for type in TYPES_TO_CLEAN:
        for brain in catalog(portal_type=type):
            object = brain.getObject()
            if object is not None:
                catalog.unindexObject(object)
            else:    
                catalog.uncatalog_object(brain.getPath())


functions = {
    'cleanIndexes': cleanIndexes,
    }

class GeneralSetup(SetupWidget):
    type = 'CompositePack Setup'

    description = """This applies a function to the site. These functions are some of the basic
set up features of a site. The chances are you will not want to apply these again. <b>Please note</b>
these functions do not have an uninstall function."""

    functions = functions

    def setup(self):
        pass

    def delItems(self, fns):
        out = []
        out.append(('Currently there is no way to remove a function', INFO))
        return out

    def addItems(self, fns):
        out = []
        for fn in fns:
            self.functions[fn](self, self.portal)
            out.append(('Function %s has been applied' % fn, INFO))
        return out

    def installed(self):
        return []

    def available(self):
        """ Go get the functions """
        return self.functions.keys()
