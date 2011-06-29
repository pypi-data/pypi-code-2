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
 ********************************************************
 ** (Un)installs a .zexp file somewhere in the portal. **
 ********************************************************


 Note : the zexp file must be in the Product's Extensions folder

 This might be an alternate way to install a workflow.

"""
__version__ = "$Revision: 20301 $"
# $Source: /cvsroot/ingeniweb/PloneSubscription/SubscriptionTool.py,v $
# $Id: ZexpInstaller.py 227919 2010-12-01 11:43:20Z glenfant $
__docformat__ = 'restructuredtext'


import os

from Globals import package_home

from Products.CMFQuickInstallerTool import  AlreadyInstalled

from utils import InstallerBase

__all__ = ('ZexpInstaller',)


class ZexpInstaller(InstallerQISupportBase):

    _installerTitle = "zexp export in portal"


    def __init__(self, zexp_filename, path, set_owner=True, **kw):
        """Constructor:
        @param zexp_filename: the file must be located in the Prooduct's Extensions folder
        @param path: the path of the object in which the import is processed. The path is
                     evaluated using "restrictedTraverse" from the portal object.
                     Use an empty string to import into the portal itself.
        @param set_owner: set the ownership of imported object(s) otherwise, keeps the ownership.
        @param kw: override defaults like stop_on_error attribute
        """
        self.zexp_filename = zexp_filename
        self.path = path
        self.set_owner = set_owner
        for k, v in kw.items():
            setattr(self, k, v)
        return


    def doInstall(self, context):
        """Installs the zexp in the path
        @param context: InstallationContext object
        """
        destination = context.portal.restrictedTraverse(self.path)
        zexp_filepath = os.path.join(package_home(context.product_globals), 'Extensions', self.zexp_filename)
        try:
            destination._importObjectFromFile(zexp_filepath, verify=True, set_owner=self.set_owner)
        except AlreadyInstalled, e:
            context.logWarning("%s is already installed. Operation skipped!" % self.zexp_filename)
        else:
            context.logInfo("ZEXP file '%s' imported into '%s'" % (self.zexp_filename, self.path))
        return
