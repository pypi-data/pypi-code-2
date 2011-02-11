# -*- coding: utf-8 -*-
## Copyright (C) 2009 Ingeniweb - Alter Way Solutions - all rights reserved
## No publication or distribution without authorization.

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
from zope.interface import implements
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class IHasardPortlet(IPortletDataProvider):
    """
    A portlet displaying a the top news
    """

class Assignment(base.Assignment):
    implements(IHasardPortlet)
    title = _(u'Au hasard')

class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('templates/hasard.pt')

    def render(self):
        return self._template()

    def hasard(self,output='portlet'):
        context = self.context
        mn_tool = getToolByName(context, 'portal_metadataNav')
        self.portal_state = getMultiAdapter((context, self.request),
                                            name=u'plone_portal_state')
        self.site_url = self.portal_state.portal_url()

        params_dict = {'XSL':output, 
                        'XSL_PARAMS':{'rss.title':u"Hasard", 
                                    'rss.desc':u'Une ressource du site au hasard',
                                    'rss.copyright':u'Mon établissement',},
                        'COLLATION':'',
                        'site_url': self.site_url,
                    }
            
        query = unicode((str(context.xq_hasard) % mn_tool.getQueryParams(params_dict, self.request)))

        da = mn_tool.getDA()

        res = da.query(query.encode('utf-8'), object_only=1)

        return str(res)

class AddForm(base.NullAddForm):
    def create(self):
        return Assignment()
