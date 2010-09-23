##############################################################################
#
# Copyright (c) 2001 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" CMFDefault portal_properties tool.

$Id: PropertiesTool.py 110659 2010-04-08 15:54:42Z tseaver $
"""

from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner, aq_parent
from Globals import InitializeClass, DTMLFile
from OFS.SimpleItem import SimpleItem
from Products.MailHost.interfaces import IMailHost
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface import implements

from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.interfaces.portal_properties \
        import portal_properties as z2IPropertiesTool
from Products.CMFCore.utils import registerToolInterface
from Products.CMFCore.utils import UniqueObject

from permissions import ManagePortal
from utils import _dtmldir


class PropertiesTool(UniqueObject, SimpleItem):

    implements(IPropertiesTool)
    __implements__ = (z2IPropertiesTool, )

    id = 'portal_properties'
    meta_type = 'Default Properties Tool'

    security = ClassSecurityInfo()

    manage_options = ( ({'label': 'Overview',
                         'action': 'manage_overview'},)
                     + SimpleItem.manage_options
                     )

    #
    #   ZMI methods
    #
    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = DTMLFile( 'explainPropertiesTool', _dtmldir )

    #
    #   'portal_properties' interface methods
    #
    security.declareProtected(ManagePortal, 'editProperties')
    def editProperties(self, props):
        '''Change portal settings'''
        site = getUtility(ISiteRoot)
        site.manage_changeProperties(**props)
        getUtility(IMailHost).smtp_host = props['smtp_server']
        if hasattr(self, 'propertysheets'):
            ps = self.propertysheets
            if hasattr(ps, 'props'):
                ps.props.manage_changeProperties(props)

    def title(self):
        site = queryUtility(ISiteRoot)
        if site is None:
            # fallback
            return aq_parent(aq_inner(self)).title
        return site.title

    def smtp_server(self):
        return getUtility(IMailHost).smtp_host

InitializeClass(PropertiesTool)
registerToolInterface('portal_properties', IPropertiesTool)
