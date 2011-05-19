# -*- coding: utf-8 -*-

from elementtree import ElementTree

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions
from Products.CMFCore.ActionInformation import Action

from collective.portaltabs import portaltabsMessageFactory as _




def _prettify(url_expr):
    if url_expr and not url_expr.startswith('python:') and not url_expr.startswith('string:'):
        return 'tal:' + url_expr
    if url_expr.startswith('string:'):
        return url_expr[7:]
    return url_expr



def _tallify(url):
    """
    Restore the TAL expression state of the url_expr
    """
    if url.startswith('tal:'):
        return url[4:]
    if url.startswith('www.'):
        url = 'http://' + url
    if not url.startswith('string:') and not url.startswith('python:'):
        return 'string:' + url
    return url



def _serialize_category_tabs(category):
    for action in category.values():
        yield {
                'id': action.id,
                'title': action.title,
                'url': _prettify(action.getProperty('url_expr', '')),
                'visible': action.getProperty('visible', False),
                }




class ManagePortaltabsView(BrowserView):

    template = ViewPageTemplateFile('manage_portaltabs.pt')

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.confirmMessage = ''
        self.errs = {}
        self.portal_actions = getToolByName(context, 'portal_actions')
        self.translation_service = getToolByName(context, 'translation_service')
        self.plone_utils = getToolByName(context, 'plone_utils')


    def translate(self, msgid, default):
        return self.translation_service.utranslate(domain = 'collective.portaltabs',
                                                   msgid = msgid,
                                                   default = default,
                                                   context = self.context)


    @property
    def confirm_message(self):
        if not self.confirmMessage:
            dummy = _(u'confirm_message', default=u'Confirm deletion?')
            confirmMessage = self.translate(msgid='confirm_message',
                                            default=u'Confirm deletion?')
            self.confirmMessage = confirmMessage
        return self.confirmMessage


    def iter_categories(self):
        """
        Generate (id, title) tuples of the managed categories.
        Non-existing categories are ignored
        """
        category_ids = self.portal_actions.keys()
        for line in getToolByName(self.context, 'portal_properties').portaltabs_settings.manageable_categories:
            try:
                id, title = line.split('|', 1)
            except ValueError:
                id = title = line
            # Be sure that the CMF Category exists
            if id in category_ids:
                yield id, title


    def iter_translated_categories(self):
        """
        Generate (id, translated_title) tuples of managed categories
        """
        for id, title in self.iter_categories():
            yield id, self.translate(msgid=title, default=title)


    @property
    def defaults(self):
        results = []
        for id, title in self.iter_translated_categories():
            results.append({'id': id, 'title': title})
        return results


    @property
    def check_disableFolderSections(self):
        """
        Check if the disable_folder_sections is on or off
        """
        return getToolByName(self.context, 'portal_properties').site_properties.disable_folder_sections


    def saved_actions(self):
        """
        Return current saved tabs
        """
        results = []
        for category_id, title in self.iter_translated_categories():
            results.append({'id': category_id, 'title': title, 'tabs': list(_serialize_category_tabs(self.portal_actions[category_id]))})
        return results


    def _validateInput(self, form):
        """
        Validate possible form input
        """
        if not form.get('title'):
            self.errs['title'] = True
        if not form.get('url'):
            self.errs['url'] = True
        return self.errs


    def form_add(self):
        form = self.request.form
        if self._validateInput(form):
            return
        category_id = form.get('action')
        title = form.get('title')
        action_id = form.get('id') or self.plone_utils.normalizeString(title)
        action = Action(action_id,
                        title=title,
                        url_expr=_tallify(form.get('url')),
                        permissions=(permissions.View,))
        self.portal_actions[category_id]._setObject(action_id, action)
        return _(u'Tab added')


    def form_save(self):
        form = self.request.form
        visible = form.get('visible')
        if self._validateInput(form):
            return
        for category_id, cat_action_id, title, url in zip(form.get('action', []),
                                                          form.get('id', []),
                                                          form.get('title', []),
                                                          form.get('urls', [])):
            action_id = cat_action_id.split('|')[1]
            action = self.portal_actions[category_id][action_id]
            action.manage_changeProperties(title = title,
                                           url_expr = _tallify(url),
                                           visible = cat_action_id in visible)
        return _(u'Change saved')


    def form_delete(self):
        ids = [self.request.get('Delete')]
        category_id = self.request.get('action')
        self.portal_actions[category_id].manage_delObjects(ids=ids)
        return _(u'Tab deleted')


    def form_upload(self):
        fin = self.request.form['file']
        tree = ElementTree.parse(fin)

        managed_categories = set(x[0] for x in self.iter_categories())

        for el in tree.findall('object'):
            if el.get('meta_type') != 'CMF Action Category':
                continue

            category_id = el.get('name')
            if category_id not in managed_categories:
                continue

            existing_category = self.portal_actions[category_id]

            for action in el.findall('object'):
                if action.get('meta_type') != 'CMF Action':
                    continue

                action_id = action.get('name')

                props = {}
                permissions = []
                for prop_el in action:
                    name = prop_el.get('name')
                    if name == 'permissions':
                        permissions = [perm.get('value') for perm in prop_el.findall('element')]
                    else:
                        props[name] = prop_el.text or ''

                if action_id in existing_category:
                    action = self.portal_actions[category_id][action_id]
                    action.manage_changeProperties(title=props['title'],
                                                   description=props['description'],
                                                   url_expr=props['url_expr'],
                                                   icon_expr=props['icon_expr'],
                                                   available_expr=props['available_expr'],
                                                   permissions=permissions,
                                                   visible=(props['visible']=='True'),
                                                   )
                else:
                    action = Action(action_id,
                                    title=props['title'],
                                    description=props['description'],
                                    url_expr=props['url_expr'],
                                    icon_expr=props['icon_expr'],
                                    available_expr=props['available_expr'],
                                    permissions=permissions,
                                    visible=(props['visible']=='True'))
                    self.portal_actions[category_id]._setObject(action_id, action)
        return _(u'File uploaded')


    def form_move(self):
        """Move a tab up or down (means left or right commonly)"""
        action_id = self.request.get('move')
        where = self.request.get('where')
        category_id = self.request.get('action')
        category = self.portal_actions[category_id]

        if where == 'top':
            category.moveObjectsToTop(ids=[action_id])
        elif where == 'up':
            category.moveObjectsUp(ids=[action_id])
        elif where == 'down':
            category.moveObjectsDown(ids=[action_id])
        elif where == 'bottom':
            category.moveObjectsToBottom(ids=[action_id])
        else:
            raise ValueError('Bad arguments for moveTab')

        return _(u'Tab moved')


    def __call__(self):
        request = self.request
        request.set('disable_border', True)
        fn = None
        msg = None

        form = request.form
        if form.get('Save'):
            fn = self.form_save
        elif form.get('Add'):
            fn = self.form_add
        elif request.get('Delete'):
            fn = self.form_delete
        elif request.get('move'):
            fn = self.form_move
        elif request.get('Upload'):
            fn = self.form_upload

        if fn:
            msg = fn()

        if msg:
            self.plone_utils.addPortalMessage(msg, type='info')
            request.response.redirect('%s/%s' % (self.context.absolute_url(), self.__name__))
        else:
            return self.template()


