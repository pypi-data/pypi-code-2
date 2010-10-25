# -*- coding: utf-8 -*-

import grokcore.viewlet as grok
from grokui.base import Header, Footer, Messages, IUIPanel, IGrokUIRealm
from grokcore.message.utils import receive
from zope.browsermenu.interfaces import IBrowserMenu
from zope.authentication.interfaces import IUnauthenticatedPrincipal
from zope.component import getUtility

grok.view(IUIPanel)
grok.context(IGrokUIRealm)
grok.templatedir("templates")


class Banner(grok.Viewlet):
    grok.order(10)
    grok.name('grokui.banner')
    grok.viewletmanager(Header)


class LoginInformation(grok.Viewlet):
    grok.order(20)
    grok.name('grokui.login')
    grok.viewletmanager(Header)

    @property
    def is_authenticated(self):
        """Check, wether we are authenticated.
        """
        return not IUnauthenticatedPrincipal.providedBy(self.request.principal)


class MenuViewlet(grok.Viewlet):
    grok.order(30)
    grok.name("grokui.menu")
    grok.viewletmanager(Header)

    def update(self):
        menu = getUtility(IBrowserMenu, "grokui_mainmenu")
        self.rooturl = self.view.url(self.context)
        self.actions = menu.getMenuItems(self.context, self.request)


class StatusMessages(grok.Viewlet):
    grok.order(40)
    grok.name('grokui.messages')
    grok.viewletmanager(Messages)

    @property
    def messages(self):
        return receive()


class Authors(grok.Viewlet):
    grok.order(10)
    grok.name('grokui.authors')
    grok.viewletmanager(Footer)
