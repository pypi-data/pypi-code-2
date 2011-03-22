import unittest

from Products.PloneTestCase.ptc import PloneTestCase
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryAdapter
from zope.site.hooks import setHooks
from zope.site.hooks import setSite

from Products.GenericSetup.utils import _getDottedName
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletType
from plone.app.portlets.storage import PortletAssignmentMapping

from betahaus.contextcloud.tests.layer import ContextCloudLayer
from betahaus.contextcloud.interfaces import IContextCloud
from betahaus.contextcloud.browser import portlet


class TestPortlet(PloneTestCase):
    """ Mostly taken from plone.app.portlets.tests - thanks """
 
    layer = ContextCloudLayer
    name = 'betahaus.contextcloud.Portlet'
    
    def afterSetUp(self):
        #Should be common for all tests
        setHooks()
        setSite(self.portal)
        self.setRoles(('Manager',))

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name=self.name)
        self.assertEquals(portlet.addview, self.name)

    def testInterfaces(self):
        assignment = portlet.Assignment()
        self.failUnless(IPortletAssignment.providedBy(assignment))
        self.failUnless(IPortletDataProvider.providedBy(assignment.data))

    def testInvokeAddview(self):
        ccportlet = getUtility(IPortletType, name=self.name)
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + ccportlet.addview)
        addview.createAndAdd(data={})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], portlet.Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = portlet.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, portlet.EditForm))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        assignment = portlet.Assignment()

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, portlet.Renderer))


class TestRenderer(PloneTestCase):

    layer = ContextCloudLayer
    name = 'betahaus.contextcloud.Portlet'

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def _some_news(self):
        news = self.portal.news
        doActionFor = self.portal.portal_workflow.doActionFor
        
        #A gloomy cloud...
        items = {
        1:[u'Slander',u'Blasphemy'],
        2:[u'Slander',u'Loose talk',u'Blasphemy'],
        3:[u'Slander',u'Loose talk',],
        4:[u'Slander',],
        5:[u'Slander',],
        6:[u'Slander',u'Loose talk',u'Uncommon niceness'],
        }
        for (i, subjects) in items.items():
            id = news.invokeFactory('News Item', id="item-%s" % str(i))
            obj = news.get(id)
            obj.update(subject=subjects)
            doActionFor(obj, 'publish')
            obj.reindexObject()

    def _renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.portal.news
        request = request or context.REQUEST
        view = view or context.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = assignment or self._assign_portlet()

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def _assign_portlet(self, **kwargs):
        """ Assign a portlet to the portal root and return the mapping.
            kwargs is data for the portlet.
        """
        mapping = PortletAssignmentMapping()
        return portlet.Assignment(**kwargs)
        

    def test_portlet_render_results(self):
        """ The portlet should provide the same results as querying the adapter directly. """
        self._some_news()
        news = self.portal.news
        assignment = self._assign_portlet(layout='cloud')
        renderer = self._renderer(context=news, assignment=assignment)
        
        #Default value will be a cloud
        portlet_results = renderer.getResults()
        self.failUnless(portlet_results)
        
        cloud = IContextCloud(news)
        adapter_results = cloud.getResults()
        #The portlet will create a cloud too if specified
        adapter_results = cloud.addCloud(adapter_results)
        
        #Comparison between the two lists must be on attribute level
        #since the objects themselves won't be the same
        comp_attrs = ['name','weight','count','url']
        for comp_attr in comp_attrs:
            self.assertEqual([getattr(x, comp_attr) for x in portlet_results],
                             [getattr(x, comp_attr) for x in adapter_results],
                             msg="Failed comparison for attribute: %s" % comp_attr)

    def test_portlet_available(self):
        """ Make sure the portlet is available in contexts where it should be.
        """
        self._some_news()
        news = self.portal.news
        
        assignment = self._assign_portlet(layout='cloud')
        renderer = self._renderer(context=news, assignment=assignment)
        
        self.assertEqual(renderer.available, True)
        
        #Using th eportlet on the document first-page shouldn't work though
        front = self.portal['front-page']
        renderer = self._renderer(context=front, assignment=assignment)
        
        self.assertEqual(renderer.available, False)

    def test_two_portlets(self):
        """ Two portlets should work in the same context for different indexes. """
        self._some_news()
        news = self.portal.news
        
        assignment1 = self._assign_portlet(layout='cloud',catalog_index='Subject')
        assignment2 = self._assign_portlet(layout='cloud',catalog_index='portal_type')
        
        renderer1 = self._renderer(context=news, assignment=assignment1)
        renderer2 = self._renderer(context=news, assignment=assignment2)
        
        #Make sure the results aren't similar - use set since they're easier to compair
        results1 = set(renderer1.getResults())
        results2 = set(renderer2.getResults())

        self.failIf(results1 == results2)
    
    def test_update_reflected(self):
        """ Make sure no implemented caches or similar get in the way when updating
            a context with more content.
        """
        self._some_news()
        news = self.portal.news
        assignment = self._assign_portlet(layout='cloud',catalog_index='Subject')
        renderer = self._renderer(context=news, assignment=assignment)
        
        results1 = renderer.getResults()
        
        #And now let's add some more content
        id = news.invokeFactory('News Item', id="new-news")
        obj = news.get(id)
        obj.update(subject=[u'New subject'])
        obj.reindexObject()

        #Hrm, is this really correct?
        renderer = self._renderer(context=news, assignment=assignment)
        results2 = renderer.getResults()

        self.failIf(set(results1) == set(results2))
        #The new renderer should have one more item
        self.assertEqual(len(results2),len(results1)+1)

    def test_memoize_cache(self):
        """ Make sure results are cached for each request"""
        self._some_news()
        news = self.portal.news
        assignment = self._assign_portlet(layout='cloud',catalog_index='Subject')
        renderer = self._renderer(context=news, assignment=assignment)
        results1 = set(renderer.getResults())
        results2 = set(renderer.getResults())
        self.assertEqual(results1, results2)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)