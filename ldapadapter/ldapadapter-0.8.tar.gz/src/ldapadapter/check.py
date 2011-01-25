##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""A LDAP Adapter Test Facility

$Id:$
"""
import zope.interface
from zope.interface import implements
from zope.security.proxy import removeSecurityProxy

from ldapadapter.interfaces import ICheckLDAPAdapter

class CheckLDAPAdapter:
    """A LDAP connection test adapter."""

    zope.interface.implements(ICheckLDAPAdapter)

    def __init__(self, context):
        self.context = context
        self.report = []
    
    def testConnection(self, bindDN, bindPassword):
        self.report = []
        adapter = removeSecurityProxy(self.context)
        serverURL = adapter.getServerURL()
        self.report.append("... start check connection")
        
        try:
            self.report.append("... try connect with:")
            self.report.append("... serverURL = %s" % serverURL)
            self.report.append("... bindDN = %s" % bindDN)
            connection = adapter.connect(bindDN, bindPassword)

            if connection:
                self.report.append("... <strong>connection OK!</strong>")
                self.report.append("... <strong>%s</strong>" % connection)
            else:
                self.report.append("... <strong>Connection None</strong>")

            return self.report

        except:
            self.report.append("... <strong>Test failed!</strong>")
            return self.report
