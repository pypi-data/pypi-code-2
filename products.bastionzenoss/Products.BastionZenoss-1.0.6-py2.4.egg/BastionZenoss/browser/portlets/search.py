#
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
from zope import schema
from zope.formlib import form
from zope.interface import implements
from Acquisition import aq_get, aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.portlet.static import PloneMessageFactory as _
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName



class ISearchPortlet(IPortletDataProvider):
    """  zentinel navigation portlet """

    base = schema.ASCIILine(title=_(u"Base URL"),
                            description=_(u"The url of the Zentinel as dispatched via ZWindow."),
                            required=True,
                            default='zentinel/show_window?url=/zport/dmd/deviceSearchResults')



class Renderer(base.Renderer):
    """ Overrides static.pt in the rendering of the portlet. """
    render = ViewPageTemplateFile('search.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    @property
    def available(self):
        return True

    def site_url(self):
	return getToolByName(self.context, 'portal_url').getPortalObject().absolute_url()


    def base_url(self):
        """
        the search url as recognised by Zenoss
        """
        return self.data.base

    def zen_search_url(self):
        """
        the search url as recognised by Zenoss
        """
        return '/zport/dmd/deviceSearchResults?query='

    def search_url(self):
        """
        the search URL
        """
        return '%s/zentinel/show_window' % self.site_url()

    def query(self):
        """
        return the ip/query the user typed in
        """
        return self.request.has_key('form.button.Query') and request.get('query','') or ''
        
class Assignment(base.Assignment):
    """ Assigner for portlet. """
    implements(ISearchPortlet)
    title = _(u'Zenoss Device/IP Search')

    def __init__(self, base):
        self.base = base

class AddForm(base.AddForm):
    form_fields = form.Fields(ISearchPortlet)
    label = _(u"Add Zenoss Device Search Portlet")
    description = _(u"This portlet provides your Zenoss device/ip search.")

    def create(self, data):
        return Assignment(data.get('base', ''),)    

class EditForm(base.EditForm):
    form_fields = form.Fields(ISearchPortlet)
    label = _(u"Edit Zenoss Device Search Portlet")
    description = _(u"This portlet provides your Zenoss device/ip search.")


