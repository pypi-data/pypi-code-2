from math import ceil
from Acquisition import aq_inner
from zope.component import getMultiAdapter
from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.navtree import buildFolderTree
from Products.CMFPlone.browser.interfaces import ISiteMap, ISitemapView
from Products.CMFPlone.browser.navtree import NavtreeQueryBuilder
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class QueryBuilder(NavtreeQueryBuilder):

    def __init__(self, context):
        NavtreeQueryBuilder.__init__(self, context)
        self.query['path'] = {'query' : "/".join(context.getPhysicalPath()),
                              'depth' : 3}


class MatrixView(BrowserView):

    implements(ISiteMap)

    def special_link(self, item):
        return {'Link': item['getRemoteUrl'],
                'File': item['getURL'].replace("view", "download"),
                'BlobFile': item['getURL'].replace("view", "download"),
                'SpeedFile': item['getURL'].replace("view", "download"),
                }.get(item['portal_type'], item['getURL'])

    def itemText(self, content):
        if content['Description']:
            return content['Description']
        elif content['Title']:
            return content['Title']
        else:
            return content['item'].getId

    def createTree(self):

        self.folders = []
        self.content = []

        context = aq_inner(self.context)
        queryBuilder = QueryBuilder(context)
        query = queryBuilder()
        strategy = getMultiAdapter((context, self), INavtreeStrategy)
        strategy.showAllParents = False
        strategy.rootPath = "/".join(context.getPhysicalPath())
        items = buildFolderTree(context, obj=context, query=query, strategy=strategy)
        for item in items['children']:
            if item['item'].is_folderish:
                self.folders.append(item)
            else:
                item['getURL'] = self.special_link(item)
                self.content.append(item)

    def format_date(self, date):
        context = aq_inner(self.context)
        util = getToolByName(context, 'translation_service')
        return util.ulocalized_time(date, True, None, context)


class MatrixDisplay(BrowserView):

    def divide(self, items):
        return int(ceil(len(items)/3.0))

    def display(self, items, filter=False, level=0, icons=False):
        if level == 2:
            template = ViewPageTemplateFile("listing_table.pt")
        else:
            template = ViewPageTemplateFile("listing_macro.pt")
        if filter:
            folders = []
            for item in items:
                if item['item'].is_folderish:
                   folders.append(item)
            return template(self, items = folders, level=level, icons=icons)
        return template(self, items = items, level=level, icons=icons)
