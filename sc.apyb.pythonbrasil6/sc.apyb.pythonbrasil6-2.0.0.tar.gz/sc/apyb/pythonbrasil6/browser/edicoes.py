# -*- code:utf-8 -*-
from zope import schema
from zope import component
from zope.component import getMultiAdapter
from Acquisition import aq_inner
from Products.Five import BrowserView

class RedirecionaEdicaoAtual(BrowserView):
    def __init__(self, context, request):
        super(RedirecionaEdicaoAtual, self).__init__(context, request)
        self.context = aq_inner(context)
        self.request = self.context.request
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        context_state = getMultiAdapter((context, self.request), name=u'plone_context_state')
        plone_tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self._context = context_state
        self.portal_url = portal_state.portal_url()
        portal_properties = plone_tools.properties()
        site_properties = getattr(portal_properties, 'site_properties')
        self.edicao = site_properties.getProperty('edicao_atual', '2011')
        
    def __call__(self):
        ''' Process Request
        '''
        response = self.request.response
        url = '%s/%s' % (self.portal_url,self.edicao)
        return response.redirect(url)

