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
 *****************************************************
 ** (Un)installation of new types in the types tool **
 *****************************************************

 Example:

     from Products.MyProduct import MyType1, MyType2, MyType3
     ...
     # Serveral types in one TypeInstaller object
     ti1 = TypeInstaller((MyType1.factory_type_information,
 MyType2.factory_type_information))
     # Only one type in one TypeInstaller object
     ti2 = TypeInstaller(MyType3.factory_type_information)
     ...

"""
__version__ = "$Revision: 20301 $"
# $Source: /cvsroot/ingeniweb/PloneSubscription/SubscriptionTool.py,v $
# $Id: TypeInstaller.py 227919 2010-12-01 11:43:20Z glenfant $
__docformat__ = 'restructuredtext'

from Products.CMFCore.TypesTool import ContentFactoryMetadata

from utils import InstallerBase

__all__ = ('TypeInstaller',)

class TypeInstaller(InstallerQISupportBase):

    _installerTitle = "content type in portal types"


    def __init__(self, fti, **kw):
        """Constructor
        @param fti: a (sequence of) usual factory type information structure(s)
        @param kw: override defaults like stop_on_error attribute
        """
        if type(fti) == type({}):
            fti = [fti]
        self.fti = tuple(fti)
        for k, v in kw.items():
            setattr(self, k, v)
        return

    def doInstall(self, context):
        """Registers the types in portal_types
        @param context: InstallationContext object
        """
        actual_type_ids = context.portal_types.objectIds()
        for fti in self.fti:
            fti_id = fti['id']
            if fti_id in actual_type_ids:
                context.logWarning("Type %s already installed in portal types, skipping" %
                                   fti_id)
            else:
                cfm = apply(ContentFactoryMetadata, (), fti)
                context.portal_types._setObject(fti_id, cfm)
                context.logInfo("Type %s installed in portal types" % fti_id)
        return
