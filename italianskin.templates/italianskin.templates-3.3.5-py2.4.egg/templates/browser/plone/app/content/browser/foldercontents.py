from zope.component import getMultiAdapter
from zope.interface import implements
from zope.i18n import translate

from AccessControl import Unauthorized
from Acquisition import aq_parent, aq_inner
from OFS.interfaces import IOrderedContainer
from Products.ATContentTypes.interface import IATTopic
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView

from plone.memoize import instance
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.content.browser.tableview import Table, TableKSSView

from Products.CMFPlone.interfaces import IPloneSiteRoot

import urllib

from plone.app.content.browser.foldercontents import FolderContentsView as OldFolderContentsView
from plone.app.content.browser.foldercontents import FolderContentsTable as OldFolderContentsTable
from plone.app.content.browser.tableview import Table as oldTable
from plone.app.content.browser.tableview import TableKSSView as oldTableKSSView
from zope.app.pagetemplate import ViewPageTemplateFile


class FolderContentsView(OldFolderContentsView):
    def contents_table(self):
        table = FolderContentsTable(aq_inner(self.context), self.request)
        return table.render()

class FolderContentsTable(OldFolderContentsTable):
    """   
    The foldercontents table renders the table and its actions.
    """                

    def __init__(self, context, request, contentFilter={}):
        self.context = context
        self.request = request
        self.contentFilter = contentFilter

        url = context.absolute_url()
        view_url = url + '/@@folder_contents'
        self.table = Table(request, url, view_url, self.items,
                           show_sort_column=self.show_sort_column,
                           buttons=self.buttons)

class FolderContentsKSSView(oldTableKSSView):
    table = FolderContentsTable

class Table(oldTable):
    render = ViewPageTemplateFile("table.pt")

