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

GROUPS = ('main', 'classes', 'browseby', 'mgmt')


class INavigationPortlet(IPortletDataProvider):
    """  zentinel navigation portlet """

    title = schema.TextLine(title=_(u"Portlet Title"),
                            description=_(u"The title of the portlet."),
                            required=True,
                            default=u'Zentinel')

    base = schema.ASCIILine(title=_(u"Base URL"),
                            description=_(u"The url of the Zentinel as dispatched via ZWindow."),
                            required=True,
                            default='zentinel/show_window?url=/zport/dmd')

    enterprise = schema.Bool(title=_(u"Enterprise"),
                             description=_(u"Indicate if this is Zenoss Enterprise rather than Zenoss Core"),
                             required=False,
                             default=False)

    additional = schema.Text(title=_(u'Additional Links'),
                             description=_(u'Colon-delimited links, tagged on group,title,link - group is one of %s. For example main:More stuff:Devices/More' % ', '.join(GROUPS)),
                             required=False,
                             default=u'')

    

class Renderer(base.Renderer):
    """ Overrides static.pt in the rendering of the portlet. """
    render = ViewPageTemplateFile('navigation.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    @property
    def available(self):
        return True

    def site_url(self):
	return getToolByName(self.context, 'portal_url').getPortalObject().absolute_url()

    def additional(self):
        """
        return a dict of the additional groupings
        """
        results = {}
        text = self.data.additional

        if text:
            for line in text.split('\n'):
                for (group,title,anchor) in line.split(':'):
                    if not results.has_key(group):
                        results[group] = [ {'title':title, 'link':anchor} ]
                    else:
                        results[group].append({'title':title, 'link':anchor})

        return results

    def base(self):
        return '%s/%s' % (self.site_url(), self.data.base)

    def enterprise(self):
        return self.data.enterprise

    def title(self):
        """
        the title of the portlet
        """
        return self.data.title
        
        
class Assignment(base.Assignment):
    """ Assigner for portlet. """
    implements(INavigationPortlet)
    title = _(u'Zentinel Menus')

    def __init__(self, title, base, enterprise, additional):
        self.title = title
        self.base = base
        self.enterprise = enterprise
        self.additional = additional

class AddForm(base.AddForm):
    form_fields = form.Fields(INavigationPortlet)
    label = _(u"Add Zentinel Navigation Portlet")
    description = _(u"This portlet provides your zentinel menus.")

    def create(self, data):
        return Assignment(data.get('title', u'Zentinel'),
                          data.get('base', ''),
                          data.get('enterprise', False),
                          data.get('additional', ''))    

class EditForm(base.EditForm):
    form_fields = form.Fields(INavigationPortlet)
    label = _(u"Edit Zentinel Navigation Portlet")
    description = _(u"This portlet provides your zentinel menus.")


