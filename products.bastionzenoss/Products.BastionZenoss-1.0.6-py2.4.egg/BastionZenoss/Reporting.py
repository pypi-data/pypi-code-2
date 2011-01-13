#
# Copyright 2010 Corporation of Balclutha (http://www.balclutha.org)
# 
#                All Rights Reserved
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
#
# Corporation of Balclutha DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS, IN NO EVENT SHALL Corporation of Balclutha BE LIABLE FOR
# ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE. 
#
import Globals
from AccessControl.Permissions import access_contents_information
from Products.CMFCore.utils import UniqueObject, getToolByName, registerToolInterface
from Products.CMFCore.permissions import View
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from zope.interface import implements

try:
    from Products.BastionBase.PortalFolder import PortalFolder
except:
    from Products.CMFPlone.PloneFolder import PloneFolder as PortalFolder

from config import ZENREPORTS_TOOL
from interfaces import IZenReportTool

class ReportsTool(UniqueObject, ActionProviderBase, PortalFolder):
    """
    The zport wrapped thingy

    This is essentially a place-holder until we fully skin Zenoss
    """
    implements(IZenReportTool)

    meta_type = portal_type = 'ZenReportsTool'

    id = ZENREPORTS_TOOL

    _actions = ()

    __ac_permissions__ = ActionProviderBase.__ac_permissions__ + (
        (View, ('availableReports',)),
        ) + PortalFolder.__ac_permissions__

    manage_options = ActionProviderBase.manage_options + PortalFolder.manage_options

    def __init__(self, id=ZENREPORTS_TOOL):
        PortalFolder.__init__(self, id, 'Zenoss Reporting Tool')

    #def zport(self):
    #    """
    #    """
    #    return self.getPhysicalRoot().zport

    #def dmd(self):
    #    """
    #    """
    #    return self.zport().dmd

    def availableReports(self):
        """
        returns a list of reports available for this particular user
        """
        results = []

        pat = getToolByName(self, 'portal_actions')

        for rpt in pat.listActionInfos(categories=('zenoss_reports',)) + self.listActionInfos():
            if rpt['visible'] and rpt['available'] and rpt['allowed']:
                results.append({'id':rpt['id'],
                                'url':rpt['url'],
                                'icon':rpt['icon'] or 'document_icon.gif',
                                'title':rpt['title'],
                                'description':rpt['description']})

        return results

    def passthruUrlBase(self):
        """
        returns the url which works to pass through the zentinel window
        """
        portal_url = getToolByName(self, 'portal_url').getPortalObject().absolute_url()
        return '%s/zentinel/show_window?url=' % portal_url

Globals.InitializeClass(ReportsTool)
registerToolInterface(ZENREPORTS_TOOL, IZenReportTool)

