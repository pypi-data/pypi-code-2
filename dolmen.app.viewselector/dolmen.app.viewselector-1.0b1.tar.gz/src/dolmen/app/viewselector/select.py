# -*- coding: utf-8 -*-

import grokcore.viewlet as grok
from grokcore import message
from megrok.layout import IPage
from dolmen.app.viewselector import MF as _, SelectableViewsMenu, IViewSelector
from dolmen.app.layout import Page, master
from dolmen.app.layout.viewlets import ContextualActions
from zope.component import queryMultiAdapter


class SelectedView(Page):
    grok.name("index")
    grok.context(IViewSelector)
    grok.require("dolmen.content.View")

    def render(self):
        rendering = queryMultiAdapter(
            (self.context, self.request), name=self.context.selected_view)
        if rendering is not None and IPage.providedBy(rendering):
            rendering.update()
            return rendering.content()
        return _(u"The selected view is not a valid IPage component.")


class ApplyView(grok.View):
    grok.name('viewselector')
    grok.context(IViewSelector)
    grok.require("dolmen.content.Edit")

    def render(self, name=None):
        if not name or name == 'index':
            message.send(
                _(u"This element can't be selected as the default view."))
        else:
            self.context.selected_view = name
            message.send(
                _(u"${name} has been selected as the default view.",
                  mapping={'name': name}))
        return self.redirect(self.url(self.context))


class SelectableViews(ContextualActions):
    grok.order(80)
    grok.context(IViewSelector)
    grok.viewletmanager(master.AboveBody)
    grok.require("dolmen.content.Edit")

    menu_factory = SelectableViewsMenu

    def compute_actions(self, viewlets):
        for action in viewlets:
            selected = action.__name__ == self.context.selected_view
            if not selected:
                url = "%s/@@viewselector?name=%s" % (
                    self.menu.context_url, action.__name__)
            else:
                url = None

            yield {
                'id': action.__name__,
                'url': url,
                'title': action.title,
                'selected': selected,
                'class': (selected and 'selected ' +
                          self.menu.entry_class or self.menu.entry_class),
                }
