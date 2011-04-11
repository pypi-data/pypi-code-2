from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from collective.portlet.foldercontents import foldercontents
from collective.portlet.foldercontents.tests.base import PortletFoldercontentsTestCase
from collective.portlet.foldercontents.scales import PortalScalesVocabularyFactory 

class TestPortlet(PortletFoldercontentsTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('Folder', 'test_folder')
        self.portal.test_folder.invokeFactory('Folder', 'subfolder1')
        self.portal.test_folder.invokeFactory('Folder', 'subfolder2')

    def test_portlet_type_registered(self):
        portlet = getUtility(IPortletType,
            name='collective.portlet.foldercontents.FolderContentsPortlet')
        self.assertEquals(portlet.addview,
            'collective.portlet.foldercontents.FolderContentsPortlet')

    def test_interfaces(self):
        portlet = foldercontents.Assignment(name=u"test name",
                                            body=u"test text",
                                            folder="test_folder",
                                            number=0)
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        portlet = getUtility(IPortletType,
        name='collective.portlet.foldercontents.FolderContentsPortlet')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        addview.createAndAdd(data={'name' : u"test name",
                                   'body' : u"test text",
                                   'folder' : "test_folder",
                                   'number' : 0})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0],
                                   foldercontents.Assignment))

    def test_invoke_edit_view(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST
        mapping['foo'] = foldercontents.Assignment(name=u"test name",
                                                          body=u"test text",
                                                          folder="test_folder",
                                                          number=0)
        editview = getMultiAdapter((mapping['foo'], request), name='edit')

        self.failUnless(isinstance(editview, foldercontents.EditForm))

    def test_obtain_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager,
                             name='plone.rightcolumn',
                             context=self.portal)
        assignment = foldercontents.Assignment(name=u"test name",
                                                      body=u"test text",
                                                      folder="test_folder",
                                                      number=0)
        renderer = getMultiAdapter((context, request, view, manager, assignment)
                                    , IPortletRenderer)

        self.failUnless(isinstance(renderer, foldercontents.Renderer))

class TestRenderer(PortletFoldercontentsTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('Folder', 'test_folder')
        self.portal.test_folder.invokeFactory('Folder', 'subfolder1')
        self.portal.test_folder.invokeFactory('Folder', 'subfolder2')

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager,
                                        name='plone.rightcolumn',
                                        context=self.portal)
        assignment = assignment or \
        foldercontents.Assignment(name=u"test name",
                                         body=u"test text",
                                         folder="test_folder",
                                         number=0)
        return getMultiAdapter((context, request, view, manager, assignment),
                                IPortletRenderer)

    def test_render(self):
        # TODO: indentation
        r = self.renderer(context=self.portal,
            assignment=foldercontents.Assignment(name=u"test name",
                                                        body=u"test text",
                                                        folder="test_folder",
                                                        number=1,
                                                        image="/logo.jpg",
                                                        image_scale="mini"))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        self.failUnless('subfolder1' in output)
        self.failIf('subfolder2' in output)
    
    def test_available(self):
        r = self.renderer(context=self.portal,
            assignment=foldercontents.Assignment(name=u"test name",
                                                        body=u"test text",
                                                        folder="/none_folder",
                                                        number=0))
        r = r.__of__(self.folder)
        r.update()
        self.failIf(r.available, True)
        r = self.renderer(context=self.portal,
            assignment=foldercontents.Assignment(name=u"test name",
                                                        body=u"test text",
                                                        folder="",
                                                        number=0))
        r = r.__of__(self.folder)
        r.update()
        self.failIf(r.available, True)
        
        r = self.renderer(context=self.portal,
            assignment=foldercontents.Assignment(name=u"test name",
                                                        body=u"test text",
                                                        folder="/",
                                                        number=0))
        r = r.__of__(self.folder)
        r.update()
        self.failIf(r.available, True)
    
    def test_getContainer(self):
        r = self.renderer(context=self.portal,
            assignment=foldercontents.Assignment(name=u"test name",
                                                        body=u"test text",
                                                        folder="/none_folder",
                                                        number=0))
        r = r.__of__(self.folder)
        r.update()
        self.failIf(r._getContainer("/none_folder") is not None)
        
        r = self.renderer(context=self.portal,
            assignment=foldercontents.Assignment(name=u"test name",
                                                        body=u"test text",
                                                        folder="test_folder",
                                                        number=0))
        r = r.__of__(self.folder)
        r.update()
        self.failIf(r._getContainer("test_folder") is None)
        
        r = self.renderer(context=self.portal,
            assignment=foldercontents.Assignment(name=u"test name",
                                                        body=u"test text",
                                                        folder="/",
                                                        number=0))
        r = r.__of__(self.folder)
        r.update()
        self.failIf(r._getContainer("/") is not None)
        
    def test_getData(self):
        r = self.renderer(context=self.portal,
            assignment=foldercontents.Assignment(name=u"test name",
                                                        body=u"test text",
                                                        folder="test_folder",
                                                        number=0,
                                                        more_url=True))
        r = r.__of__(self.folder)
        r.update()
        folder_url = self.portal.absolute_url() + "/test_folder"
        
        self.assertEqual(r.getData()["header"], u"test name")
        self.assertEqual(r.getData()["more_url"], folder_url)
        self.assertEqual(len(r.getData()["contents"]), 2)
        self.assertEqual(r.getData()["image"], None)
        
        r = self.renderer(context=self.portal,
            assignment=foldercontents.Assignment(name=u"test name",
                                                        body=u"test text",
                                                        folder="test_folder",
                                                        number=1,
                                                        image="/logo.jpg",
                                                        more_url=False))
        r = r.__of__(self.folder)
        r.update()
        self.assertEqual(r.getData()["more_url"], "")
        self.assertEqual(len(r.getData()["contents"]), 1)
        self.failUnless("/logo.jpg" in r.getData()["image"]["url"])
 

class TestVocabulary(PortletFoldercontentsTestCase):   
    
    def test_vocabulary(self):
        ptool = self.portal.portal_properties
        props = getattr(ptool, 'imaging_properties', None)
        if props is not None:
            # vocabulary must have all default scales values
            vocabulary = PortalScalesVocabularyFactory(self.portal)
            scales_values = vocabulary.by_value.keys()
            scales_values.sort()
            self.assertEqual(scales_values, ['icon','large','listing','mini',
                                                   'preview','thumb','tile'])
            
            iprops = self.portal.portal_properties.imaging_properties
            iprops.manage_changeProperties(allowed_sizes=['valid_scale 23:23'])
            vocabulary = PortalScalesVocabularyFactory(self.portal)
            scales_values = vocabulary.by_value.keys()
            self.assertEqual(scales_values, ['valid_scale'])
            
            # vocabulary must not have valid scale
            iprops.manage_changeProperties(
                allowed_sizes=['not_valid_scale 23:23*'])
            vocabulary = PortalScalesVocabularyFactory(self.portal)
            self.assertEqual(vocabulary.by_value.keys(), [])
        else:
            vocabulary = PortalScalesVocabularyFactory(self.portal)
            scales_values = vocabulary.by_value.keys()
            self.assertEqual(scales_values, [])
  
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    suite.addTest(makeSuite(TestVocabulary))
    return suite