# -*- coding: utf-8 -*-

import transaction

from zope.component import getUtility
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.pathtouid.interfaces import IUIDConverted
from collective.pathtouid import pathfixMessageFactory as _

class ConvertUIDView(BrowserView):
    """Vista dei file nella vista modulistica"""
    
    template = ViewPageTemplateFile('browser.pt')
    
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        request.set('disable_border', True)
    
    def __call__(self):
        putils = getToolByName(self.context, 'plone_utils')
        if self.request.form.get('Confirm'):
            self.request.response.redirect(self.context.absolute_url())
            self._fixSubTree(self.request.form)
            if self.request.form.get('dry'):
                putils.addPortalMessage(_(u'Dry run selected. No change mades'), type='error')
            return
        return self.template()
    
    def _fixSubTree(self, form):
        context = self.context
        catalog = getToolByName(context, 'portal_catalog')
        putils = getToolByName(context, 'plone_utils')
        results = catalog(portal_type=form.get('portal_type','Document'),
                          path='/'.join(context.getPhysicalPath()))
        converter = getUtility(IUIDConverted)
        counter = 0
        for x in results:
            obj = x.getObject()
            text = obj.getText()
            changesDone = False
            # Absolute URLs
            if form.get('absolute') and converter.findAbsolutePath(text):
                newtext = converter.absolutePathToUID(text)
                if newtext!=text:
                    putils.addPortalMessage(_(u'Absolute path fixed for ${path}',
                                              mapping={'path': x.getPath()}))
                    text = newtext
                    changesDone = True
            # Relative URLs
            if form.get('relative') and converter.findRelativePath(text):
                newtext = converter.relativePathToUID(text, obj)
                if newtext!=text:
                    putils.addPortalMessage(_(u'Relative path fixed for ${path}',
                                              mapping={'path': x.getPath()}))
                    text = newtext
                    changesDone = True
            # Lets do something
            if changesDone:
                counter+=1
            if changesDone and not form.get('dry', False):
                obj.setText(text)
                if counter % 100 == 0:
                    transaction.savepoint(optimistic=True)
        putils.addPortalMessage(_(u'${count} content modified',
	                          mapping={'count': counter}))
        context.plone_log('%s contents modified' % counter)
