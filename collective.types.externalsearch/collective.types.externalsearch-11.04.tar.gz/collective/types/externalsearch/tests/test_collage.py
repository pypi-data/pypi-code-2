from collective.types.externalsearch.tests import base
from Testing import ZopeTestCase as ztc
from collective.types.externalsearch import ExternalSearch
#from collective.types.externalsearch.browser.external_search import
#View as ESView

try:
    #Get the Collage view manager if it's available
    from Products.Collage.browser.renderer import SimpleContainerRenderer as ESView
    from Products.Collage.interfaces import IDynamicViewManager as CollageManager
except:
    pass
    
def installCollage():
    #Install Collage
    ztc.installProduct('Collage')
    ztc.installProduct('collective.types.externalsearch')

class TestCollageNotAdded(base.TypesFunctionalTestCase):
    """Collage has not been added, make sure the
    views for collage are not set up.
    """
    def afterSetUp(self):
        self.folder.invokeFactory('Folder', 'externalsearchCollageNotInstalled')
        self.folder = getattr(self.folder,
                              'externalsearchCollageNotInstalled')

    def testViewNotAvailable(self):
        """The Collage view should not be available
        """
        self.folder.invokeFactory('collective.types.ExternalSearch',
                                  'externalsearchNoCollage')
        es = self.folder.externalsearchNoCollage
        layouts = [x[0] for x in es.getAvailableLayouts()]
        self.assertTrue('view' in layouts,
                        '%s was not in the avilable views for ExternalSearch: %s' % ('view_page', es.getAvailableLayouts()))
        self.assertFalse('standard' in layouts,
                        '%s should not have been in the avilable views for ExternalSearch: %s' % ('standard', es.getAvailableLayouts()))

class TestCollageAdded(base.TypesFunctionalTestCase):
    """Collage has been added, make sure the views for
    Collage are set up.
    """
    def afterSetUp(self):
        installCollage()
        self.portal.portal_quickinstaller.installProduct('Collage')
        self.portal.portal_quickinstaller.installProduct('collective.types.externalsearch')

        self.folder.invokeFactory('Folder', 'externalsearchCollageInstalled')
        self.folder = getattr(self.folder,
                             'externalsearchCollageInstalled')

    def testViewAvailable(self):
        """The Collage view should be available
        """

        self.folder.invokeFactory('Collage', id='collage')
        collage = self.folder.collage

        collage.invokeFactory('CollageRow', 'row')
        collage.row.invokeFactory('CollageColumn', 'column')
        column = collage.row.column
        column.invokeFactory('collective.types.ExternalSearch',
                             'externalsearchCollage')
        es = column.externalsearchCollage

        #Get the Collage layout manager for es
        manager = CollageManager(es)

        layouts = [x[0] for x in manager.getLayouts()]

        #view_page is in the list of Plone layouts, it
        #shouldn't be in this list
        self.assertFalse('view_page' in layouts,
                         '%s should not be in the avilable Collage views for ExternalSearch: %s' % ('view_page', es.getAvailableLayouts()))

        #standard is what Collage uses for the default view.
        #We set this up in browser/collage.zcml
        self.assertTrue('standard' in layouts,
                        '%s should have been in the avilable views for ExternalSearch: %s' % ('standard', es.getAvailableLayouts()))

        esView = ESView(collage, self.folder.REQUEST)
        text = esView.getItems()[0]()

        #Make sure error is not displayed
        self.assertFalse('Error:' in text,
                         'There was an error: %s' % text)

        #Make sure the search string was built
        self.assertTrue('external_search_externalsearchCollage' in text,
                        'Search string was not built')
        

def test_suite():
    #Only run this suite of tests if Collage is available
    try:
        from Products import Collage
    except:
        print """Warning: collective.types.externalsearch
        could not be tested with Collage because Collage
        is not available"""
        return
    
    from unittest import TestSuite
    from unittest import makeSuite

    suite = TestSuite()
    suite.addTest(makeSuite(TestCollageNotAdded))
    suite.addTest(makeSuite(TestCollageAdded))
    #suite.addTest(makeSuite(TestViewMethods))
    
    return suite

