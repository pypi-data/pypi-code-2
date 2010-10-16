from Acquisition import aq_inner

from zope.component import getMultiAdapter

from plone.memoize.instance import memoize
from plone.app.portlets.portlets import navigation as base
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.interfaces import INavigationQueryBuilder

from Products.CMFPlone import PloneMessageFactory as _

from navtree import buildFolderTree

class Renderer(base.Renderer):
    """ Renderer that uses a custom navtree builder
    """

    @memoize
    def getNavTree(self, _marker=[]):
        context = aq_inner(self.context)
        
        queryBuilder = getMultiAdapter(
            (context, self.data), INavigationQueryBuilder)
        strategy = getMultiAdapter((context, self.data), INavtreeStrategy)

        return buildFolderTree(context, obj=context, query=queryBuilder(),
            strategy=strategy)
