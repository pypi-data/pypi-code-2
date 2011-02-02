# -*- coding: utf-8 -*-

import grokcore.view as grok

from dolmen import menu
from dolmen.app import security, layout
from dolmen.app.container import MF as _
from megrok.z3ctable import TablePage, LinkColumn, ModifiedColumn, table
from zope.dublincore.interfaces import IDCDescriptiveProperties

from ZODB.broken import PersistentBroken
from zope.container.interfaces import IContainer
from zope.component import queryMultiAdapter
from zope.i18n import translate
from zope.interface import Interface

grok.templatedir("templates")


@menu.menuentry(layout.ContextualMenu, order=40)
class FolderListing(TablePage):
    grok.title(_(u"Content"))
    grok.context(IContainer)
    grok.require(security.CanListContent)

    batchSize = 20
    startBatchingAt = 20
    cssClassEven = u'even'
    cssClassOdd = u'odd'
    cssClasses = {'table': 'listing sortable'}
    sortOn = None
    label = _("Content of the folder")

    @property
    def values(self):
        return self.context.values()

    def update(self):
        TablePage.update(self)
        self.table = self.renderTable()
        self.batch = self.renderBatch()


class Title(LinkColumn):
    """Displays the title of the item.
    """
    table(FolderListing)
    grok.context(Interface)
    grok.name('folderlisting.title')

    weight = 10
    header = _(u"Title")

    def getLinkContent(self, item):
        dc = IDCDescriptiveProperties(item, None)
        if dc is not None and dc.title:
            return dc.title
        return LinkColumn.getLinkContent(self, item)

    def renderCell(self, item):
        if isinstance(item, PersistentBroken):
            broken = _(
                "Broken item: ${name}",
                mapping={"name": item.__Broken_state__.get('__name__')})
            return translate(broken)

        icon_view = queryMultiAdapter((item, self.request), name="icon")
        if icon_view is not None:
            return "%s %s" % (icon_view(), LinkColumn.renderCell(self, item))
        return LinkColumn.renderCell(self, item)


class ModificationDate(ModifiedColumn):
    """Displays the last modification date.
    """
    table(FolderListing)
    grok.context(Interface)
    grok.name('folderlisting.modified')

    weight = 20
    header = _(u"Modification date")

    def renderCell(self, item):
        value = ModifiedColumn.renderCell(self, item)
        return value or u""
