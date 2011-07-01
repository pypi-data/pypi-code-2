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

 ******************************************
 ** (un)installs an External method (EM) **
 ******************************************

 Examples:

 # Installs 'amId' external method in the Plone root

 emi = ExternalMethodInstaller('%s.SomeModule' % PROJECTNAME, 'aFunction', 'emId')

 # Installs 'amId' external method in the Zope root

 emi = ExternalMethodInstaller('%s.SomeModule' % PROJECTNAME, '/aFunction', 'emId')

 # Installs 'amId' external method in the Plone root deleting any object
 # of same name if any

 emi = ExternalMethodInstaller('%s.SomeModule' % PROJECTNAME, 'aFunction', 'emId', force=True)


"""
__version__ = "$Revision: 20301 $"
# $Source: /cvsroot/ingeniweb/PloneSubscription/SubscriptionTool.py,v $
# $Id: ExternalMethodInstaller.py 227919 2010-12-01 11:43:20Z glenfant $
__docformat__ = 'restructuredtext'


from utils import InstallerBase

__all__ = ('ExternalMethodInstaller',)

class ExternalMethodInstaller(InstallerBase):
    """Will create an external method for you"""
    
    _installerTitle = "External method in portal"


    def __init__(self,module, function, path, title="", roles=(), force=False, **kw):
        """Constructor
        @param module: string as in the ZMI form
        @param function: as in the ZMI form
        @param name path: portal relative or absolute path for the external method
        @param title: as in the ZMI
        @param roles: role(s) who can execute that EM.
        @param force: True: deletes prior any object that may have that path.
                      False: issues a warning if an existing object has that path.
        @param kw: override defaults like stop_on_error attribute
        """
        self.module = module
        self.function = function
        self.path = path
        self.title = title
        if type(roles) == type(''):
            roles = [roles]
        self.roles = list(roles)
        self.force = force
        for k, v in kw.items():
            setattr(self, k, v)
        return


    def doInstall(self, context):
        """Installs the external method
        @param contex: installation context
        """
        base, em_id = self._splitPath(context, self.path)
        addExtenalMethod = base.manage_addProduct['ExternalMethod'].manage_addExternalMethod
        if self.force and hasattr(base, em_id):
            base._delObject(em_id)
        if not hasattr(base, em_id):
            addExtenalMethod(em_id, self.title, self.module, self.function)
            if self.roles:
                # Assign these roles only to View (execute) permission
                em = getattr(base, em_id)
                em.manage_permission('View', roles=self.roles)
        else:
            context.logError("Couldn't install '%s' external method, an object with same id already exists"
                             % self.path)
        return


    def doUninstall(self, context):
        """Uninstalls the external method
        @param contex: installation context
        """
        base, em_id = self._splitPath(context, self.path)
        if hasattr(base, em_id):
            base._delObject(em_id)
        else:
            context.logWarning("The '%s' External method couldn't be found" % self.path)
        return


    def _splitPath(self, context, path):
        """-> container base, name
        Example path = 'foo/bar/beer' -> 'foo/bar' object, 'beer'
        """
        if self.path.startswith('/'):
            base = context.portal.getPhysicalRoot()
        else:
            base = context.portal
        base = base.restrictedTraverse('/'.join(path.split('/')[:-1]))
        return base, path.split('/')[-1]
