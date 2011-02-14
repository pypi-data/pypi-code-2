#!/usr/bin/python
# -*- coding: utf-8 -*-

import grokcore.view as grok

from dolmen import menu
from dolmen.app.container import listing
from dolmen.app.layout import Page
from dolmen.app.viewselector import SelectableViewsMenu
from megrok.layout.interfaces import IPage
from menhir.contenttype.folder import IFolder
from menhir.contenttype.folder import MCFMessageFactory as _
from zope.component import queryMultiAdapter
from zope.publisher.defaultview import queryDefaultViewName


@menu.menuentry(SelectableViewsMenu)
class ContentListingView(listing.FolderListing):
    grok.name('listing')
    grok.context(IFolder)
    grok.title(_('label_folder_contents', default='Content of the folder'))


@menu.menuentry(SelectableViewsMenu)
class CompositeView(Page):
    grok.context(IFolder)
    grok.title(_('label_summary_view', default='Summary view'))

    def update(self):
        self.items = []
        for item in self.context.values():
            name = queryDefaultViewName(item, self.request, self.context)
            if name is not None:
                view = queryMultiAdapter((item, self.request), name=name)
                if view is not None and IPage.providedBy(view):
                    view.update()
                    self.items.append(view.content())
