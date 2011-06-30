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
 ** Executes external methods at install and uninstall time **
 *************************************************************

 This doesn't directly install anything special but runs a serie
 of external methods at install time and another one at uninstall

 Examples:

 # Executes one external method at install time only

 emr = ExternalMethodRunner(ext_install=('SomeProduct.ExternalModule', 'function1))

 # Executes 2 external methods at install time and one at uninstall time

 emr = ExternalMethodRunner(ext_install=(('SomeProduct.ExternalModule', 'function1),
                                         ('SomeProduct.ExternalModule', 'function2)),
                            ext_uninstall=('SomeProduct.ExternalModule', 'function3))


"""
__version__ = "$Revision: 20301 $"
# $Source: /cvsroot/ingeniweb/PloneSubscription/SubscriptionTool.py,v $
# $Id: ExternalMethodRunner.py 227919 2010-12-01 11:43:20Z glenfant $
__docformat__ = 'restructuredtext'

from Products.ExternalMethod.ExternalMethod import ExternalMethod

from utils import InstallerBase

__all__ = ('ExternalMethodRunner',)

class ExternalMethodRunner(InstallerBase):
    """Runs series of external methods at install and/or uninstall time"""

    _installerTitle = "by running External method in portal"
    
    
    def __init__(self, ext_install=(), ext_uninstall=(), **kw):
        """Constructor
        @param ext_install: tuple or tuple of tuples as ('module', 'function')
                            executed at install time
        @param ext_uninstall: tuple or tuple of tuples as ('module', 'function')
                              executes at uninstall time
        @param kw: override defaults like stop_on_error attribute
        """
        self.ext_install = self._fixType(ext_install)
        self.ext_uninstall = self._fixType(ext_uninstall)
        for k, v in kw.items():
            setattr(self, k, v)
        return
    

    def doInstall(self, context):
        """Run external methods in the portal context at install time
        @param context: InstallationContext object
        """
        for module_name, function_name in self.ext_install:
            self._runExternalMethod(context, module_name, function_name)
        return

    def doUninstall(self, context):
        """Run external methods in the portal context at un install time
        @param context: InstallationContext object
        """
        for module_name, function_name in self.ext_uninstall:
            self._runExternalMethod(context, module_name, function_name)
        return

    def _fixType(self, collection):
        """Makes an a tuple of tuples or empty tuple
        @param collection: empty list, single tuple or 
        """
        # Wahh. This is ugly but it works
        if collection == ():
            return collection
        if type(collection[0]) is type(''):
            # Single external method tuple
            return (collection,)
        # Supposed to be a tuple or list of tuples
        return collection
    
    def _runExternalMethod(self, context, module_name, function_name):
        """Runs an external method in context of the portal.
        @param context: InstallationContext object
        @param module_name: as in ZMI for eternal methods
        @param function_name: as in ZMI for eternal methods
        """
        function = ExternalMethod('temp', 'temp', module_name, function_name)
        context.logInfo("Below the log of External Method '%s' of module '%s'" %
                        (function_name, module_name))
        context.logInfo(function(context.portal))
        return
