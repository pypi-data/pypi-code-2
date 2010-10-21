##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces.browser import IBrowserRequest,IBrowserSkinType
from zope.component import getGlobalSiteManager
from zope.publisher.interfaces import IRequest
import zope.interface
import urllib

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.security.proxy import removeSecurityProxy
from zope.interface import providedBy
from zope.session.interfaces import ISession
from zope.app import zapi

from z3c.securitytool.securitytool import settingsForObject
from z3c.securitytool.securitytool import MatrixDetails, PrincipalDetails, PermissionDetails
from z3c.securitytool.interfaces import ISecurityChecker, IPrincipalDetails, IPermissionDetails

SESSION_KEY = 'securitytool'

class PrincipalMatrixView(BrowserView):
    """ This is the view used to populate the vum.html
        (securitytool main page)
    """

    pageTemplateFile = "viewprincipalmatrix.pt"

    evenOddClasses = ('even','odd')
    evenodd = 0

    def __call__(self):
        self.update()
        return self.render()

    def update(self):
        skin = self.handleSkinSelection()
        perm = self.handlePermissionSelection()

        ifaces = tuple(providedBy(self.context))
        security_checker = ISecurityChecker(self.context)

        # Here we populate the viewMatrix
        self.viewMatrix, self.views, self.permissions = \
            security_checker.getPermissionSettingsForAllViews(ifaces, skin,
            perm)
        self.path = '/'.join(
                        self.request.get('REQUEST_URI','').split('/')[2:-1])
        self.sortViews()

    def render(self):
        return  ViewPageTemplateFile(self.pageTemplateFile)(self)

    def handleSkinSelection(self):
        """ This method handles the logic for the selectedSkin
            widget and session storage for the widget
        """
        selectedPermission = None
        formSkin   = self.request.form.get('selectedSkin','')
        sessionSkin= ISession(self.request)[SESSION_KEY].get('selectedSkin','')
        defaultSkin= self.skinTypes.items()[0][0]

        if formSkin:
            selectedSkin = formSkin
        elif sessionSkin:
            selectedSkin = sessionSkin
        else:
            selectedSkin = defaultSkin

        skin = zapi.getUtility(IBrowserSkinType,selectedSkin)
        ISession(self.request)[SESSION_KEY]['selectedSkin'] = selectedSkin
        
        return skin

    def handlePermissionSelection(self):
        """ This method handles the logic for the selectedPermission
            widget and session storage for the widget
        """
        
        formPerm = self.request.form.get('selectedPermission','')
        sessionPerm= ISession(self.request)[SESSION_KEY].get(
                                                'selectedPermission','')
        
        if formPerm:
            if formPerm  == u'None':
                selectedPermission = ''
            else:
                selectedPermission = formPerm
        else:
            selectedPermission = sessionPerm or ''

        ISession(self.request)[SESSION_KEY]['selectedPermission'] = \
                                                     selectedPermission
        return selectedPermission        

    def sortViews(self):
        """ self.views is a dict in the form of {view:perm}
            Here It would make more sense to group by permission
            rather than view
        """
        self.viewList = {}
        sortedPerms = sorted([(v,k) for k,v in self.views.items()])

        for item in sortedPerms:
            if self.viewList.has_key(item[0]):
                self.viewList[item[0]].append(item[1])
            else:
                self.viewList[item[0]] = [item[1]]

    def cssclass(self):
        """ determiner what background color to use for lists """
        if self.evenodd != 1:
            self.evenodd = 1
        else:
            self.evenodd = 0
        return self.evenOddClasses[self.evenodd]

    def getPermissionSetting(self, view, principal):
        try:
            return self.viewMatrix[principal][view]
        except KeyError:
            return '--'

    @property
    def skinTypes(self):
        """ gets all the available skins on the system """
        skinNames = {}
        for name, util in zapi.getUtilitiesFor(IBrowserSkinType, self.context):
            skinNames[name] = False
            if (self.request.form.has_key('selectedSkin') and
                self.request.form['selectedSkin'] == name):
                skinNames[name] = True
        return skinNames

    @property
    def urlEncodedViewName(self):
        """ properly formats variables for use in urls """
        urlNames = {}
        for key in self.views.keys():
            urlNames[key] = urllib.quote(key)
        return urlNames

    def getPermissionList(self):
        """ returns sorted permission list"""
        return sorted(self.permissions)

class PrincipalDetailsView(BrowserView):
    """ view class for ud.html (User Details)"""
    pageTemplateFile = "principalinfo.pt"

    def update(self):
        self.principal = self.request.get('principal','no principal specified')
        skin = getSkin(self.request) or IBrowserRequest

        principal_security = PrincipalDetails(self.context)
        self.principalPermissions = principal_security(self.principal,
                                                       skin=skin)

        self.legend = (u"<span class='Deny'>Red Bold = Denied Permission"
                       u"</span>,<span class='Allow'> Green Normal = "
                       u"Allowed Permission </span>")

        self.preparePrincipalPermissions()

    def preparePrincipalPermissions(self):
        """
        This method just organized the permission and role tree
        lists to display properly.
        """
        permTree = self.principalPermissions['permissionTree']
        for idx, item in enumerate(permTree):
            for uid,value in item.items():
                if value.has_key('permissions'):
                    self.principalPermissions['permissionTree']\
                                      [idx][uid]['permissions'].sort()
                    self.principalPermissions['permissionTree']\
                                      [idx][uid]['parentList'].reverse()

        permTree = self.principalPermissions['roleTree']
        for idx, item in enumerate(permTree):
            for uid,value in item.items():

                if value.has_key('roles'):
                    self.principalPermissions['roleTree']\
                                 [idx][uid]['roles'].sort()
                    self.principalPermissions['roleTree']\
                                 [idx][uid]['parentList'].reverse()

    def render(self):
        return ViewPageTemplateFile(self.pageTemplateFile)(self)

    def __call__(self):
        self.update()
        return self.render()

class PermissionDetailsView(BrowserView):
    """ view class for ud.html (User Details)"""
    pageTemplateFile = "permdetails.pt"

    def update(self):
        self.principal = self.request.get('principal','no user specified')
        self.view = self.request.get('view','no view specified')
        self.skin = getSkin(self.request) or IBrowserRequest


        permAdapter = zapi.getMultiAdapter((self.context,
                                            ),IPermissionDetails)

        self.principalPermissions = permAdapter(self.principal,
                                             self.view,
                                             self.skin)


        self.legend = (u"<span class='Deny'>Red Bold = Denied Permission"
                       u"</span>,<span class='Allow'> Green Normal = "
                       u"Allowed Permission </span>")

        self.preparePrincipalPermissions()

    def preparePrincipalPermissions(self):
        """
        This method just organized the permission and role tree
        lists to display properly.
        """
        permTree = self.principalPermissions['permissionTree']
        for idx, item in enumerate(permTree):
            for uid,value in item.items():
                if value.has_key('permissions'):
                    self.principalPermissions['permissionTree']\
                                      [idx][uid]['permissions'].sort()
                    self.principalPermissions['permissionTree']\
                                      [idx][uid]['parentList'].reverse()

        permTree = self.principalPermissions['roleTree']
        for idx, item in enumerate(permTree):
            for uid,value in item.items():

                if value.has_key('roles'):
                    self.principalPermissions['roleTree']\
                                 [idx][uid]['roles'].sort()
                    self.principalPermissions['roleTree']\
                                 [idx][uid]['parentList'].reverse()

    def render(self):
        return ViewPageTemplateFile(self.pageTemplateFile)(self)

    def __call__(self):
        self.update()
        return self.render()


def getSkin(request):
    """Get the skin from the session."""
    sessionData = ISession(request)[SESSION_KEY]
    selectedSkin = sessionData.get('selectedSkin', IBrowserRequest)
    return zapi.queryUtility(IBrowserSkinType, selectedSkin)
