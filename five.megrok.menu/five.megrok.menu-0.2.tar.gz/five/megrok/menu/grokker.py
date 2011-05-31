# -*- coding: utf-8 -*-
"""
five.megrok.menu

Licensed under the GPL license, see LICENCE.txt for more details.

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
import martian
from martian.error import GrokError

import grokcore.component
import grokcore.view
from zope.security.checker import CheckerPublic
from grokcore.view.meta.views import ViewSecurityGrokker, default_view_name

from zope.configuration.exceptions import ConfigurationError
from zope.app.publisher.browser.menumeta import menuDirective, \
    menuItemDirective, subMenuItemDirective

from zope.publisher.interfaces.browser import IDefaultBrowserLayer

import five.megrok.menu


class MenuGrokker(martian.ClassGrokker):
    martian.component(five.megrok.menu.Menu)
    martian.priority(1500)
    martian.directive(grokcore.component.name, get_default=default_view_name)
    martian.directive(grokcore.component.title, default=u'')
    martian.directive(grokcore.component.description, default=u'')

    def execute(self, factory, config, name, title, description, **kw):
        menuDirective(config, id=name, class_=factory,
                      title=title, description=description)
        return True


class SubMenuItemGrokker(martian.ClassGrokker):
    martian.component(five.megrok.menu.SubMenuItem)

    # We want to do this after MenuGrokker.
    martian.priority(1000)

    martian.directive(grokcore.component.name, get_default=default_view_name)
    martian.directive(grokcore.component.title, default=u'')
    martian.directive(grokcore.component.description, default=u'')
    martian.directive(grokcore.component.context)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.security.require, name='permission')

    martian.directive(five.megrok.menu.menuitem)

    def execute(self, factory, config, name, title, description, \
                    menuitem=None, context=None, layer=None, permission=None):
        menuDirective(config, id=name, class_=factory,
                      title=title, description=description)

        if menuitem is None:
            return False

        menu_id, icon, filter, order, extra = menuitem
        try:
            menu = config.resolve('zope.app.menus.%s' % menu_id)
        except ConfigurationError:
            raise GrokError("The %r menu could not be found.  Please use "
                            "megrok.menu.Menu to register a menu first."
                            % menu_id, factory)
        if permission is None:
            permission = CheckerPublic

        subMenuItemDirective(config, menu=menu, for_=context, submenu=name,
                          title=title, description=description, icon=icon,
                          filter=filter, permission=permission, layer=layer,
                          order=order, action='', extra=extra)

        return True


class MenuItemGrokker(ViewSecurityGrokker):
    martian.directive(five.megrok.menu.menuitem)
    martian.directive(grokcore.component.context)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.component.name, get_default=default_view_name)
    martian.directive(grokcore.component.title, default=u'')
    martian.directive(grokcore.component.description, default=u'')

    def execute(self, factory, config, permission, context=None,
                layer=None, name=u'', menuitem=None, description=u'',
                title=u''):
        if menuitem is None:
            return False
        menu_id, icon, filter, order, extra, action, menuContext = menuitem

        try:
            menu = config.resolve('zope.app.menus.%s' % menu_id)
        except ConfigurationError:
            raise GrokError("The %r menu could not be found.  Please use "
                            "megrok.menu.Menu to register a menu first."
                            % menu_id, factory)
        if permission is None:
            permission = CheckerPublic

        if action is None:
            action = name

        if menuContext is not None:
            context = menuContext

        menuItemDirective(config, menu=menu, for_=context, action=action,
                          title=title, description=description, icon=icon,
                          filter=filter, permission=permission, layer=layer,
                          order=order, extra=extra)

        return True
