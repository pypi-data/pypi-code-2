##############################################################################
#
# Copyright (c) 2004-2006 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""
$Id: CPpermissions.py 238389 2011-04-30 22:57:12Z hathawsh $
"""
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.permissions import setDefaultRoles
from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import AddPortalContent

DesignCompo = 'Design Composite Page'
setDefaultRoles(DesignCompo, ('Manager',))

ManageCompositePack = 'Manage Composite Pack'
setDefaultRoles(ManageCompositePack, ('Manager',))
