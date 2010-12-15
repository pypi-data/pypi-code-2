# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions
from Products.CMFCore.ActionInformation import Action

from collective.portaltabs import portaltabsMessageFactory as _

class ManagePortaltabsView(BrowserView):
    
    template = ViewPageTemplateFile('manage_portaltabs.pt')

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.confirmMessage = ''

    @property
    def confirm_message(self):
        if not self.confirmMessage:
            dummy = _(u'confirm_message', default=u"Confirm deletion?")
            translation_service = getToolByName(self.context,'translation_service')
            confirmMessage = translation_service.utranslate(domain='collective.portaltabs',
                                                            msgid='confirm_message',
                                                            default=u"Confirm deletion?",
                                                            context=self.context)
            self.confirmMessage = confirmMessage
        return self.confirmMessage

    @property
    def defaults(self):
        context = self.context
        structure = getToolByName(context, 'portal_properties').portaltabs_settings.manageable_categories
        translation_service = getToolByName(context,'translation_service')
        portal_actions = getToolByName(context, 'portal_actions')
        results = []
        for x in structure:
            if x.find("|")>-1:
                id, title = x.split("|")
            else:
                id = title = x
            title = translation_service.utranslate(domain='collective.portaltabs',
                                                   msgid=title,
                                                   default=title,
                                                   context=context)
            # Be sure that the CMF Category exists
            try:
                portal_actions[id]
            except KeyError:
                continue
            results.append({'id': id, 'title': title})
        return results

    @property
    def check_disableFolderSections(self):
        """Check is the disable_folder_sections is on or off"""
        return getToolByName(self.context, 'portal_properties').site_properties.disable_folder_sections

    def _prettify(self, url_expr):
        if url_expr and not url_expr.startswith('python:') and not url_expr.startswith('string:'):
            return 'tal:' + url_expr
        if url_expr.startswith('string:'):
            return url_expr[7:]
        return url_expr
        
    def _simplify(self, action):
        tabs = []
        for x in action.items():
            t = x[1]
            tabs.append({'id': t.id,
                         'title': t.title,
                         'url': self._prettify(t.getProperty('url_expr','')),
                         'visible': t.getProperty('visible', False),
                         })
        return tabs
    
    def _tallify(self, url):
        """Restore the TAL expression state of the url_expr"""
        if url.startswith("tal:"):
            return url[4:]
        if url.startswith("www."):
            url = 'http://' + url
        if not url.startswith("string:") and not url.startswith("python:"):
            return "string:" + url
        return url
    
    def actions(self):
        """Return current saved tabs"""
        context = self.context
        portal_actions = getToolByName(context, 'portal_actions')
        translation_service = getToolByName(context,'translation_service')
        results = []
        for value in self.defaults:
            id = value['id']
            #title = value['title']
            title = translation_service.utranslate(domain='collective.portaltabs',
                                             msgid=value['title'],
                                             default=value['title'],
                                             context=context)
            results.append({'id': id, 'title': title, 'tabs': self._simplify(portal_actions[id])})
        return results
    
    def update(self, form):
        """Update existings"""
        portal_actions = getToolByName(self.context, 'portal_actions')
        actions = form.get('action', [])
        ids = form.get('id', [])
        titles = form.get('title', [])
        urls = form.get('url', [])
        visibles = form.get('visible', [])
        i = 0
        for a in actions:
            action_category = portal_actions[a]
            action_category[ids[i].split("|")[1]].manage_changeProperties(**{'title': titles[i],
                                                               'url_expr': self._tallify(urls[i]),
                                                               'visible': ids[i] in visibles,
                                                               })
            i+=1
        return _(u'Change saved')
    
    def _generateId(self, st):
        """Generate an Id"""
        ptool = getToolByName(self.context, 'plone_utils')
        return ptool.normalizeString(st)
    
    def addNew(self, form):
        """Add a new portal tab entry"""
        portal_actions = getToolByName(self.context, 'portal_actions')
        action = form.get('action')
        title = form.get('title')
        id = form.get('id') or self._generateId(title)
        url = form.get('url')
        ac = Action(id, title=title, url_expr=self._tallify(url), permissions=(permissions.View,))
        portal_actions[action]._setObject(id, ac)
        return _(u'Tab added')
    
    def delete(self, id, category):
        """Delete a tab"""
        portal_actions = getToolByName(self.context, 'portal_actions')
        portal_actions[category].manage_delObjects(ids=[id])
        return _(u'Tab deleted')
    
    def moveTab(self, id, where, action):
        """Move a tab up or down (meas left or right commonly)"""
        portal_actions = getToolByName(self.context, 'portal_actions')
        category = portal_actions[action]
        if where=='top':
            category.moveObjectsToTop(ids=[id])
        elif where=='up':
            category.moveObjectsUp(ids=[id])
        elif where=='down':
            category.moveObjectsDown(ids=[id])
        elif where=='bottom':
            category.moveObjectsToBottom(ids=[id])
        else:
            raise ValueError("Bad arguments for moveTab")
        return _(u'Tab moved')
    
    def __call__(self):
        self.request.set('disable_border', True)
        if self.request.form.get('Save'):
            msg = self.update(self.request.form)
        elif self.request.form.get('Add'):
            msg = self.addNew(self.request.form)
        elif self.request.get('Delete'):
            msg = self.delete(self.request.get('Delete'), self.request.get('action')) 
        elif self.request.get('move'):
            msg = self.moveTab(self.request.get('move'), self.request.get('where'), self.request.get('action'))
        else:
            msg = ''
        if msg:
            ptool = getToolByName(self.context, 'plone_utils')
            ptool.addPortalMessage(msg, type='info')
            self.request.response.redirect(self.context.absolute_url()+'/'+self.__name__)
            return
        return self.template()

