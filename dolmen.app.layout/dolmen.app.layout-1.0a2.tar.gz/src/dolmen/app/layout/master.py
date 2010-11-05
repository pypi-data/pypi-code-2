# -*- coding: utf-8 -*-

import grokcore.viewlet as grok
from dolmen.app.layout import interfaces as API
from megrok.layout import Layout
from megrok.resourceviewlet import ResourcesManager
from zope.interface import Interface, moduleProvides

grok.templatedir('templates')


class Master(Layout):
    grok.name('master')
    grok.context(Interface)

    def update(self):
        self.base = str(self.request.URL.get(-1))


class Resources(ResourcesManager):
    grok.name('dolmen.resources')
    grok.context(Interface)


class Header(grok.ViewletManager):
    grok.name("dolmen.header")
    grok.context(Interface)


class Top(grok.ViewletManager):
    grok.name("dolmen.top")
    grok.context(Interface)


class Footer(grok.ViewletManager):
    grok.name("dolmen.footer")
    grok.context(Interface)


class AboveBody(grok.ViewletManager):
    grok.name("dolmen.above.body")
    grok.context(Interface)


class BelowBody(grok.ViewletManager):
    grok.name("dolmen.below.body")
    grok.context(Interface)


moduleProvides(API.IGlobalUI)
__all__ = list(API.IGlobalUI)
