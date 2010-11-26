# Customized Navigation Portlet for EGO
# created 2010/07/20 by Patrick Heck (heckp@uni-trier.de) 
# http://plone.org/documentation/kb/customizing-the-navigation-portlet-in-plone-3

from plone.app.portlets.portlets.navigation import Renderer
from plone.app.portlets.portlets.navigation import INavigationPortlet
from plone.app.portlets.portlets.navigation import NavtreeStrategy
from plone.app.portlets.portlets.navigation import INavigationPortlet
from plone.app.portlets.portlets.navigation import Assignment
from plone.app.portlets.portlets.navigation import AddForm
from plone.app.portlets.portlets.navigation import EditForm
from plone.app.portlets.portlets.navigation import QueryBuilder
from plone.app.portlets.portlets.navigation import getRootPath

from zope.interface import implements, Interface
from zope.component import adapts, getMultiAdapter, queryUtility

from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form

from plone.memoize.instance import memoize

from Acquisition import aq_inner, aq_base, aq_parent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from Products.CMFPlone.interfaces import INonStructuralFolder, IBrowserDefault
from Products.CMFPlone import utils
from Products.CMFPlone import PloneMessageFactory as _

from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.interfaces import INavigationQueryBuilder

from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.layout.navigation.navtree import buildFolderTree

from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

from Products.CMFPlone.browser.navtree import SitemapNavtreeStrategy
from Products.CMFPlone.browser.navtree import NavtreeStrategyBase

class IEgoNavtreeStrategy(Interface):
    def test():
        return True

class EgoNavRenderer(Renderer):
    
    _template = ViewPageTemplateFile('templates/navigation.pt')
    recurse = ViewPageTemplateFile('templates/navigation_recurse.pt')
    
    @memoize
    def getNavTree(self, _marker=[]):
        context = aq_inner(self.context)

        # Special case - if the root is supposed to be pruned, we need to
        # abort here

        # queryBuilder = getMultiAdapter((context, self.data), INavigationQueryBuilder)
        strategy = getMultiAdapter((context, self.data), INavtreeStrategy)
		
		# query={} makes the tree return all children of all branches with unlimited depth
        return buildFolderTree(context, obj=context, query={}, strategy=strategy)