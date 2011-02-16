# takeaction: content as actions
# Copyright (C) 2007 Jarn AS
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
from zope.interface import implements
from persistent import Persistent

from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from AccessControl.Permissions import view
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem

from Products.CMFCore.ActionInformation import ActionInfo
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.permissions import ManagePortal

try:
    from Products.LinguaPlone.interfaces import ITranslatable
except ImportError:
    from Products.CMFPlone.interfaces.Translatable import ITranslatable

from interfaces import ITakeActionTool


# Keep working across many Plone versions
translatabe = (hasattr(ITranslatable, 'isImplementedBy') and 
    ITranslatable.isImplementedBy or 
    ITranslatable.providedBy)


class TakeActionItem(Persistent):
    path = None
    category = 'take_actions'
    
    def __init__(self, path, category=None):
        self.path = path
        if category is not None:
            self.category = category
            
    def __hash__(self):
        return hash((self.path, self.category))
    
    def __cmp__(self, other):
        return cmp((self.path, self.category), (other.path, other.category))
    
    def __repr__(self):
        return '<TakeActionItem (%r, %r)>' % (self.path, self.category)

class TakeActionTool(UniqueObject, SimpleItem, ActionProviderBase):
    """TakeAction tool; designate content as actions"""
    
    implements(ITakeActionTool)
    
    if hasattr(ActionProviderBase, '__implements__'):
        # older CMF implementations
        __implements__ = ActionProviderBase.__implements__
    
    id = "portal_takeaction"
    meta_type = 'TakeAction content-as-actions tool'
    _items = ()
    
    manage_options = (
        (dict(label='Items', action='manage_main'),) +
        SimpleItem.manage_options)
    security = ClassSecurityInfo()

    security.declarePublic('listActionInfos')
    def listActionInfos(self, action_chain=None, object=None,
                        check_visibility=1, check_permissions=1,
                        check_condition=1, max=-1, categories=None):
        # List ActionInfo objects.
        # (method is without docstring to disable publishing)
        #
        ec = self._getExprContext(object)
        actions = self.listActions(object=object, categories=categories)
        actions = [ ActionInfo(action, ec) for action in actions ]

        if action_chain:
            filtered_actions = []
            if isinstance(action_chain, basestring):
                action_chain = (action_chain,)
            for action_ident in action_chain:
                sep = action_ident.rfind('/')
                category, id = action_ident[:sep], action_ident[sep+1:]
                for ai in actions:
                    if id == ai['id'] and category == ai['category']:
                        filtered_actions.append(ai)
            actions = filtered_actions

        action_infos = []
        for ai in actions:
            if check_visibility and not ai['visible']:
                continue
            if check_permissions and not ai['allowed']:
                continue
            if check_condition and not ai['available']:
                continue
            action_infos.append(ai)
            if max + 1 and len(action_infos) >= max:
                break
        return action_infos

    
    security.declarePrivate('listActions')
    def listActions(self, info=None, object=None, categories=None):
        portal = getToolByName(self, 'portal_url').getPortalObject()
        actions = []
        ids = set()
        for i, item in enumerate(self._items):
            if categories and item.category not in categories:
                # Filter on category
                continue
            # No point in using the catalog here, as we are trying to find
            # the correct translation
            content = portal.unrestrictedTraverse(item.path, None)
            if content is None or not IContentish.providedBy(content):
                continue
            content_id = content.getId()
            if translatabe(content):
                translation = content.getTranslation()
                if translation is None:
                    # Try falling back to a language-neutral version
                    translation = content.getTranslation('')
                if translation is None:
                    continue
                content = translation
            if not getSecurityManager().checkPermission(view, content):
                continue
            # Ensure that we use a unique id for our action
            id = 'takeaction-%s' % content_id
            idcount = 1
            while id in ids:
                idcount += 1
                id = 'takeaction-%s-%d' % (content_id, idcount)
            ids.add(id)
            action = ActionInformation(
                id,
                content.Title(),
                content.Description(),
                item.category,
                action='string:' + content.absolute_url())
            actions.append(action)
        return actions
    
    security.declareProtected(ManagePortal, 'addAction')
    def addAction(self, path, category=None):
        """Add a new TakeAction content item"""
        item = TakeActionItem(path, category)
        
        if item in set(self._items):
            raise ValueError('Duplicate item (%r, %r)' % (path, category))
        self._items += (item,)
        
    security.declareProtected(ManagePortal, 'deleteAction')
    def deleteAction(self, path, category=None):
        """Delete a TakeAction content item"""
        item = TakeActionItem(path, category)
        self._items = tuple(i for i in self._items if i != item)
        
    security.declareProtected(ManagePortal, '')
            
InitializeClass(TakeActionTool)
