##############################################################################
#
# Copyright (c) 2004-2006 Zope Corporation and Contributors.
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
"""View Class for the Container's Contents view.

$Id:$
"""
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.publisher.browser import BrowserView

from ldapadapter.interfaces import IManageableLDAPAdapter
from ldapadapter.interfaces import ICheckLDAPAdapter


class CheckLDAPAdapterView(BrowserView):

    __used_for__ = IManageableLDAPAdapter

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.__parent__ = context
        self.report = []

    def getHostInfo(self):
        """Returns a dict with host information."""
        infoDict = {}
        infoDict['host'] = self.context.host
        infoDict['port'] = self.context.port
        infoDict['bindDN'] = self.context.bindDN
        infoDict['bindPassword'] = self.context.bindPassword
        infoDict['useSSL'] = self.context.useSSL and 'Yes' or 'No'
        return infoDict


    def checkConnection(self):
        """Check connetction to the given LDAP server."""
        if self.request.get('runDefault', None):
            dn = self.context.bindDN
            pw = self.context.bindPassword
            testadapter = ICheckLDAPAdapter(self.context)
            self._addInfo("<strong>"
                          "Test python connection and LDAP server binding"
                          "</strong>")
            self.report = self.report + testadapter.testConnection(dn, pw)
            self._addInfo("<strong>Tests done</strong>")
            self._addInfo(" ")
    
            return self.report

        elif self.request.get('runAnonymous', None):
            dn = ''
            pw = ''
            testadapter = ICheckLDAPAdapter(self.context)
            self._addInfo("<strong>"
                          "Test python connection and LDAP server binding"
                          "</strong>")
            self.report = self.report + testadapter.testConnection(dn, pw)
            self._addInfo("<strong>Tests done</strong>")
            self._addInfo(" ")
            return self.report
        else:
            return ""

    def _addInfo(self, res):
        """Add traceback info to the report list"""
        self.report.append(res)

    check = ViewPageTemplateFile('check.pt')
