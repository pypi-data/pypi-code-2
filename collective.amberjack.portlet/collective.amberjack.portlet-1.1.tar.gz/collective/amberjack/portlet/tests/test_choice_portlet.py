from zope.component import getUtility, getMultiAdapter, getSiteManager

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping
from collective.amberjack.portlet import amberjackchoiceportlet
from collective.amberjack.portlet.tests.base import TestCase

class TestPortletRegistered(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def test_portlet_type_registered(self):
        sm = getSiteManager()
        portlet = sm.getUtility(
            IPortletType,
            name='collective.amberjack.portlet.AmberjackChoicePortlet')
        self.assertEquals(portlet.addview,
                          'collective.amberjack.portlet.AmberjackChoicePortlet')

class TestPortlet(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def test_portlet_type_registered(self):
        sm = getSiteManager()
        portlet = sm.getUtility(
            IPortletType,
            name='collective.amberjack.portlet.AmberjackChoicePortlet')
        self.assertEquals(portlet.addview,
                          'collective.amberjack.portlet.AmberjackChoicePortlet')

    def test_interfaces(self):
        # TODO: Pass any keyword arguments to the Assignment constructor
        portlet = amberjackchoiceportlet.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        portlet = getUtility(
            IPortletType,
            name='collective.amberjack.portlet.AmberjackChoicePortlet')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        # TODO: Pass a dictionary containing dummy form inputs from the add
        # form.
        # Note: if the portlet has a NullAddForm, simply call
        # addview() instead of the next line.
        addview.createAndAdd(data={})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0],
                                   amberjackchoiceportlet.Assignment))

    def test_invoke_edit_view(self):
        # NOTE: This test can be removed if the portlet has no edit form
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = amberjackchoiceportlet.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, amberjackchoiceportlet.EditForm))

    def test_obtain_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn',
                             context=self.portal)

        # TODO: Pass any keyword arguments to the Assignment constructor
        assignment = amberjackchoiceportlet.Assignment()

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, amberjackchoiceportlet.Renderer))


class TestRenderer(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            IPortletManager, name='plone.rightcolumn', context=self.portal)

        # TODO: Pass any default keyword arguments to the Assignment
        # constructor.
        assignment = assignment or amberjackchoiceportlet.Assignment()
        return getMultiAdapter((context, request, view, manager, assignment),
                               IPortletRenderer)

    def test_render(self):
        # TODO: Pass any keyword arguments to the Assignment constructor.
        r = self.renderer(context=self.portal,
                          assignment=amberjackchoiceportlet.Assignment())
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        # TODO: Test output

class TestValidators(TestCase):
    """Test to ensure only valid tours are in portlet"""

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def test_pass(self):
        pass

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortletRegistered))
    #suite.addTest(makeSuite(TestPortlet))
    #suite.addTest(makeSuite(TestRenderer))
    #suite.addTest(makeSuite(TestValidators))
    return suite
