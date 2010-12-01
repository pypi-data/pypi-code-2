# -*- coding: utf-8 -*-
## ProductName
## Copyright (C)2006 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
 *************************************************************
 ** (Un)installer for a property sheet in portal_properties **
 *************************************************************

 Example:

     ...
     myProperties = (
         ('title', 'A specific property sheet', 'string'),
         ('myValue', 100, 'int'))
     psi = PropertysheetInstaller('my_propertysheet', myProperties)
     ...

 Note: If the 'title' string property is not provided, a title with the
 id's value is provided.

"""
__version__ = "$Revision: 20301 $"
# $Source: /cvsroot/ingeniweb/PloneSubscription/SubscriptionTool.py,v $
# $Id: PropertysheetInstaller.py 227919 2010-12-01 11:43:20Z glenfant $
__docformat__ = 'restructuredtext'


from OFS.ObjectManager import BadRequestException

from utils import InstallerBase

__all__ = ('PropertysheetInstaller',)

class PropertysheetInstaller(InstallerBase):
    """(Un)installer for a property sheet in portal_properties
    """

    _installerTitle = "Propertysheet in portal properties"


    def __init__(self, sheet_name, properties, **kw):
        """Constructor
        @param sheet_name: the name as appearing in portal_properties
        @param properties: a sequence of (id, value, type) tuples as expected by manage_addProperty
        @param kw: override defaults like stop_on_error attribute
        """
        self.sheet_name = sheet_name
        self.properties = properties
        for k, v in kw.items():
            setattr(self, k, v)
        return


    def doInstall(self, context):
        """Adds the property sheet
        @param context: an InstallationContext object
        """
        title = self.sheet_name
        for id, value, tipe in self.properties:
            if id == 'title' and tipe == 'string':
                title = value
        try:
            context.portal_properties.addPropertySheet(self.sheet_name, title=title)
            context.logInfo("Created '%s' property sheet" % self.sheet_name)
        except BadRequestException, e:
            context.logWarning("'%s' property sheet is already in portal properties, skipped"
                               % self.sheet_name)
        else:
            propertySheet = getattr(context.portal_properties, self.sheet_name)
            for id, value, tipe in self.properties:
                if id != 'title':
                    propertySheet.manage_addProperty(id, value, tipe)
            context.logInfo("Added property sheet '%s' to portal_properties" % self.sheet_name)
        return


    def doUninstall(self, context):
        """Removing the property sheet
        @param context: an InstallationContext object
        """
        try:
            context.portal_properties.manage_delObjects(ids=self.sheet_name)
            context.logInfo("Removed property sheet '%s' from portal properties" % self.sheet_name)
        except BadRequestException, e:
            context.logWarning("Property sheet '%s' already removed from portal properties" % self.sheet_name)
        return
