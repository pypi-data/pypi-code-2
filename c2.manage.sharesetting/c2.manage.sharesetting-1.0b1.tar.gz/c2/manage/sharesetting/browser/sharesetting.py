#!/usr/bin/env python
# encoding: utf-8
"""
sharesetting.py

Created by Manabu Terada on 2011-04-05.
Copyright (c) 2011 CMScom. All rights reserved.
"""
from Acquisition import aq_inner, aq_parent, aq_base
from zope.component import getUtilitiesFor, getMultiAdapter
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.workflow.interfaces import ISharingPageRole

IGNORE_GROUPS = ['Administrators', 'AuthenticatedUsers']

def _has_role(role, group, dic):
    return role in dic.get(group, [])

def _inherited(obj):
    """Return True if local roles are inherited here.
    """
    if getattr(aq_base(obj), '__ac_local_roles_block__', None):
        return False
    return True


class ShareSettingControlPanel(BrowserView):
    template = ViewPageTemplateFile('sharesetting.pt')

    def __call__(self):
        self.portal_obj = getToolByName(self, 'portal_url').getPortalObject()
        if self.request.form.get('form.localRoleSubmited') == '1':
            self.update_local_roles()
        return self.template()

    def get_groups(self):
        gtool = getToolByName(self, 'portal_groups')
        groups = gtool.listGroups()
        return [g.id for g in groups if g.id not in IGNORE_GROUPS]

    def _get_child_items(self, path):
        catalog = getToolByName(self, 'portal_catalog')
        query = {}
        query['path'] = {'query' : path, 'depth' : 1}
        query['sort_on'] = 'getObjPositionInParent'
        reviewstate = self.request.form.get('reviewstate', 'all')
        if reviewstate != 'all':
            query['review_state'] = reviewstate
        for item in catalog(query):
            yield item
            if item.is_folderish:
                for i in self._get_child_items(path=path+'/'+item.id):
                    yield i

    def get_items(self):
        path = '/'.join(self.portal_obj.getPhysicalPath())
        for item in self._get_child_items(path=path):
            yield dict(title=item.Title, url=item.getURL(), 
                    p_type=item.Type, state=item.review_state,
                    filter_role=self.request.form.get('filter_role', u'Reader'),
                    item=item,)


    def _share_setting(self, obj, group, local_roles, inherited_roles):
        role = self.request.form.get('filter_role', u'Reader')
        chk = ''
        if _has_role(role, group, local_roles):
            chk = '1'
        elif _has_role(role, group, inherited_roles): 
            chk = '2'
        return dict(group=group, chk=chk)

    def _inherited_roles(self, obj):
        if not _inherited(obj):
            return {}
        if obj == self.portal_obj:
            return {}
        cont = True
        roles = {}
        pobj = aq_parent(obj)
        while cont:
            for k, v in pobj.get_local_roles():
                roles.setdefault(k, set()).update(v)
            if not _inherited(pobj):
                cont = False
            elif pobj == self.portal_obj:
                cont = False
            else:
                pobj = aq_parent(pobj)
        return roles

    def get_item_share(self, obj):
        groups = self.get_groups()
        local_roles = dict(obj.get_local_roles())
        inherited_roles = self._inherited_roles(obj)
        for group in groups:
            yield self._share_setting(obj, group, local_roles, inherited_roles)


    def get_path_len(self, obj):
        portal_len = len(self.portal_obj.getPhysicalPath())
        obj_len = len(obj.getPhysicalPath())
        path_len = obj_len - portal_len
        return "shareSettingPathLen" + str(path_len)
    
    def get_all_review_state(self):
        wtool = getToolByName(self, 'portal_workflow')
        return [s for s in wtool.listWFStatesByTitle(filter_similar=True)]
        
    def get_all_local_role(self):
        return [name for name, utility in getUtilitiesFor(ISharingPageRole)]
        
    def _uid_to_content(self, uid):
        uid_catalog = getToolByName(self, 'uid_catalog')
        items = uid_catalog(UID=uid)
        if len(items) != 1:
            raise
        return items[0].getObject()

    def _get_submited_roles(self):
        entries = self.request.form.get('entries', [])
        groups = self.get_groups()
        for entry in entries:
            yield dict(id=entry['uid'],
                       role=entry['role'],
                       groups=[g for g in groups if entry.get('group_%s' % g, False)],
                       )

    def update_local_roles(self):
        managed_roles = frozenset(self.get_all_local_role())
        managed_groups = frozenset(self.get_groups())
        for entry in self._get_submited_roles():
            changed = False
            obj = self._uid_to_content(entry['id'])
            role = entry['role']
            old_local_roles = dict(obj.get_local_roles())
            setting_groups = frozenset(entry.get('groups', []))
            for g in managed_groups:
                set_roles = set(old_local_roles.get(g, []))
                if g in setting_groups:
                    if role not in set_roles:
                        set_roles.update([role])
                        changed = True
                elif role in set_roles:
                    set_roles.remove(role)
                    changed = True
                if changed and set_roles:
                    obj.manage_setLocalRoles(g, list(set_roles))
                elif changed and not set_roles:
                    obj.manage_delLocalRoles(userids=[g])
            if changed:
                obj.reindexObjectSecurity()
    


