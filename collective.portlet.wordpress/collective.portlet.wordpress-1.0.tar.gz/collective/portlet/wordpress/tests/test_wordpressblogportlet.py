import os, sys
import socket
import signal
import subprocess

from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from collective.portlet.wordpress import wordpress

from collective.portlet.wordpress.tests.base import PortletWordPressBlogTestCase


class TestPortlet(PortletWordPressBlogTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))

    def test_portlet_type_registered(self):
        portlet = getUtility(
            IPortletType,
            name='collective.portlet.wordpress.WordPressBlogPortlet')
        self.assertEquals(portlet.addview,
                          'collective.portlet.wordpress.WordPressBlogPortlet')

    def test_interfaces(self):
        portlet = wordpress.Assignment(name=u'Portlet header',
                                       url=u'http://testurl',
                                       wait=5,
                                       limit=5,
                                       show_more=True)
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        portlet = getUtility(
            IPortletType,
            name='collective.portlet.wordpress.WordPressBlogPortlet')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        addview.createAndAdd(data={'name' : u'Portlet header',
                                   'url' : u'http://testurl',
                                   'wait' : 5,
                                   'limit' : 5,
                                   'show_more' : True})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0],
                                   wordpress.Assignment))

    def test_invoke_edit_view(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST
        mapping['foo'] = wordpress.Assignment(name=u'Portlet header',
                                              url=u'http://testurl',
                                              wait=5,
                                              limit=5,
                                              show_more=True)
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, wordpress.EditForm))

    def test_obtain_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn',
                             context=self.portal)
        assignment = wordpress.Assignment(name=u'Portlet header',
                                          url=u'http://testurl',
                                          wait=5,
                                          limit=5,
                                          show_more=True)
        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)
        
        self.failUnless(isinstance(renderer, wordpress.Renderer))


class TestRenderer(PortletWordPressBlogTestCase):

    def resFilesPath(self):
        current_dir = os.path.dirname(__file__)
        path_to_test_res = os.path.sep.join([current_dir] + ['data', 'test'])
        path_to_not_xml_res = os.path.sep.join([current_dir] +
                                                ['data', 'not_xml'])
        path_to_dummy_server = os.path.sep.join([current_dir] +
                                                ['dummy_server.py'])
        test_url = unicode('file://' + path_to_test_res)
        not_xml_url = unicode('file://' + path_to_not_xml_res)
        return [test_url, not_xml_url, path_to_dummy_server]

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = assignment or wordpress.Assignment(name=u'Portlet header',
                                                        url=u'http://testurl',
                                                        wait=5,
                                                        limit=5,
                                                        show_more=True)
        return getMultiAdapter((context, request, view, manager, assignment),
                               IPortletRenderer)
    
    def test_render(self):
        test_url = self.resFilesPath()[0]
        not_xml_url = self.resFilesPath()[1]
        r = self.renderer(context=self.portal,
            assignment=wordpress.Assignment(name=u'Portlet header',
                url=u'http://testurl', wait=5, limit=5, show_more=True))
        r = r.__of__(self.folder)
        r.update()
        self.failIf(r.available)
        
        r = self.renderer(context=self.portal,
            assignment=wordpress.Assignment(name=u'Portlet header',
                url=not_xml_url, wait=5, limit=5, show_more=True))
        r = r.__of__(self.folder)
        r.update()
        self.failIf(r.available)
        
        r = self.renderer(context=self.portal,
            assignment=wordpress.Assignment(name=u'Portlet header',
                url=test_url, wait=5, limit=5, show_more=True))
        r = r.__of__(self.folder)
        r.update()
        self.failUnless(r.available)
        
        output = r.render()
        self.assertEqual('First Blog Post' in output, True)
        self.assertEqual('Second Blog Post' in output, True)
        
    def test_getBlogEntries(self):
        test_url = self.resFilesPath()[0]
        r = self.renderer(context=self.portal,
            assignment=wordpress.Assignment(name=u'Portlet header',
                url=test_url, wait=5, limit=5, show_more=True))
        r = r.__of__(self.folder)
        r.update()
        data = r.getBlogEntries()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0].keys(), ['url', 'date', 'desc', 'title'])
        self.assertEqual(data[1].keys(), ['url', 'date', 'desc', 'title'])
        self.assertEqual(data[0]['title'], 'First Blog Post')
        self.assertEqual(data[1]['url'],
                        'http://test.wordpress.com/2011/04/05/First-Blog-Post/')
        
        r = self.renderer(context=self.portal,
            assignment=wordpress.Assignment(name=u'Portlet header',
                url=test_url, wait=5, limit=1, show_more=True))
        r = r.__of__(self.folder)
        r.update()
        data = r.getBlogEntries()
        self.assertEqual(len(data), 1)
        
    def test_timeout(self):
        '''This test is for case when portlet sends request to server and
        server doesn't send answer for a long time'''
        python_path = sys.executable
        path_to_dummy_server = self.resFilesPath()[2]
        
        # find a free_port to start test server
        temp_server = socket.gethostbyname(socket.gethostname())
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        temp_socket.bind((temp_server, 0))
        free_port = temp_socket.getsockname()[1]
        temp_socket.close()
        
        # execute test server in subprocess
        sub_server = subprocess.Popen([python_path, path_to_dummy_server,
            str(free_port)], shell=False, stdout=subprocess.PIPE,
            stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # wait until server starts
        sub_server.stdout.readline()
        
        # create server url
        server_url = 'http://127.0.0.1:%s/' % free_port
        
        # set timeout value to be more then server makes pause. In this case we
        # expect to receive a correct data.
        r = self.renderer(context=self.portal,
            assignment=wordpress.Assignment(name=u'Portlet header',
                url=server_url, wait=20, limit=1, show_more=True))
        r = r.__of__(self.folder)
        self.assertEqual(r.available, True)
        
        # set timeout value less then server makes pause. In this case we expect
        # portlet to raise timeout error and return nothing.
        r = self.renderer(context=self.portal,
            assignment=wordpress.Assignment(name=u'Portlet header',
                url=server_url, wait=2, limit=1, show_more=True))
        r = r.__of__(self.folder)
        r.update()
        self.assertEqual(r.available, False)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
