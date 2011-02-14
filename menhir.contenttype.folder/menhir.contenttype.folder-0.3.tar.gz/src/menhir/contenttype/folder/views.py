#!/usr/bin/python
# -*- coding: utf-8 -*-

import grokcore.view as grok

from dolmen import menu
from dolmen.app.container import listing
from dolmen.app.layout import Page
from dolmen.app.viewselector import SelectableViewsMenu
from menhir.contenttype.folder import IFolder
from zope.component import getMultiAdapter
from menhir.contenttype.folder import MCFMessageFactory as _


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
            view = getMultiAdapter((item, self.request), name="index")
            view.update()
            self.items.append(view.content())
