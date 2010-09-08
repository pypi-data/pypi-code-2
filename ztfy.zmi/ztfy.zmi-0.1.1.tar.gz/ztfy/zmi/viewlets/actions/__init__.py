### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
from zope.app import zapi
from zope.app.publisher.interfaces.browser import IBrowserMenu, IMenuItemType
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.i18n import translate
from zope.interface import implements
from zope.traversing.browser.absoluteurl import absoluteURL

# import local packages
from ztfy.skin.menu import MenuItem
from ztfy.skin.viewlet import ViewletBase

from ztfy.scheduler import _


def getMenuItemType(id):
    return zapi.getUtility(IMenuItemType, id)

def getMenuEntries(menu, object, request):
    """Return menu item entries in a TAL-friendly form."""
    items = []
    for name, item in zapi.getAdapters((object, request), getMenuItemType(menu.id)):
        if item.available():
            items.append(item)
    result = []
    for item in items:
        result.append({'title': item.title,
                       'action': item.action,
                       'selected': (item.selected() and u'selected') or u'',
                       'order': item.order })
    result.sort(key=lambda x: x['order'])
    return result


class ActionMenuItem(MenuItem):
    """ZMI action menu item"""

    def __init__(self, context, request, view, manager, menu_entry):
        super(ActionMenuItem, self).__init__(context, request, view, manager)
        self.menu_entry = menu_entry

    @property
    def title(self):
        return self.menu_entry['title']

    @property
    def viewURL(self):
        return self.menu_entry['action']


class ActionsViewlet(ViewletBase):
    """Actions viewlet"""

    @property
    def viewlets(self):
        menu = zapi.getUtility(IBrowserMenu, self.menu)
        entries = getMenuEntries(menu, self.context, self.request)
        return [ActionMenuItem(self.context, self.request, self.__parent__, self, entry) for entry in entries]


class ZmiViewsMenuViewlet(ActionsViewlet):
    """zmi_views menu viewlet"""

    @property
    def title(self):
        return translate(_("Management"), context=self.request)


class ZmiActionsMenuViewlet(ActionsViewlet):
    """zmi_actions menu viewlet"""

    @property
    def title(self):
        return translate(_("Console"), context=self.request)
