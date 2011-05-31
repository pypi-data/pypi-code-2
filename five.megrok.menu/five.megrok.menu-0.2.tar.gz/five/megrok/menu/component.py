# -*- coding: utf-8 -*-
"""
five.megrok.menu

Licensed under the ZPL license, see LICENCE.txt for more details.

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
import martian.util
import grokcore.component
from martian.error import GrokImportError
from zope.app.publisher.browser.menu import BrowserMenu


class Menu(BrowserMenu):
    pass


class SubMenuItem(BrowserMenu):
    pass


class menuitem(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE

    def factory(self, menu, icon=None, filter=None, order=0, extra=None,\
                action=None, context=None):
        if martian.util.check_subclass(menu, Menu):
            menu = grokcore.component.name.bind().get(menu)
        if martian.util.not_unicode_or_ascii(menu):
            raise GrokImportError(
                "You can only pass unicode, ASCII, or a subclass "
                "of megrok.menu.Menu to the '%s' directive." % self.name)
        return (menu, icon, filter, order, extra, action, context)
