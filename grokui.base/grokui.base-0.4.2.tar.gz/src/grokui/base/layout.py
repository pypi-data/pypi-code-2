# -*- coding: utf-8 -*-

import megrok.menu
import grokcore.view as grok

from grokui.base import IGrokUIRealm, GrokUILayer, IUIPanel, MainMenu
from megrok.layout import Layout, Page
from zope.traversing.browser.absoluteurl import absoluteURL

grok.layer(GrokUILayer)


class GrokUILayout(Layout):
    """The general layout for the administration
    """
    grok.context(IGrokUIRealm)
    title = u"Grok User Interface"

    def update(self):
        self.baseurl = absoluteURL(self.context, self.request) + '/'


class GrokUIView(Page):
    """A grok ui view.
    """
    grok.baseclass()
    grok.context(IGrokUIRealm)
    grok.implements(IUIPanel)
    megrok.menu.menuitem(MainMenu)
