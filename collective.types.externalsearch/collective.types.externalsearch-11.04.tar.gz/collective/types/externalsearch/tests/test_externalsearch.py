from zope.annotation.interfaces import IAnnotations
from unittest import TestSuite

from collective.types.externalsearch.tests import base
from collective.types.externalsearch import ExternalSearch
from collective.types.externalsearch import config
from collective.types.externalsearch.interfaces import IExternalSearch

from collective.types.externalsearch.browser.external_search import View

from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.standard import url_quote
from Testing import makerequest

def buildFakeRequest(context, engine, searchString, site=''):
    REQUEST = context.REQUEST
    REQUEST['engine'] = engine
    REQUEST['site'] = site
    REQUEST['searchString'] = searchString
    REQUEST.AUTHENTICATED_USER='blah'

    return REQUEST

class TestCreateExternalSearch(base.TypesTestCase):
    """Make sure we can create External Searches
    """

    def testCreateExternalSearch(self):
        self.folder.invokeFactory('collective.types.ExternalSearch',
                                  id='test_search')
        es = self.folder.test_search
        self.assertEquals('test_search', es.id,
                          "es id should be 'test_search', "\
                          "instead it's %s" % es.id)

class TestBuildSearch(base.TypesTestCase):
    """Make sure that build_search handles inputs as
    expected
    """
    #from collective.types.externalsearch.content.externalsearch import SEARCHDICT

    def afterSetUp(self):
        self.folder.invokeFactory('collective.types.ExternalSearch',
                                  'es')
        self.search = self.folder.es

    def testNoSite(self):
        REQUEST = buildFakeRequest(self.search,
                                   'google',
                                   'search string',
                                   site='')
        info, search_string = self.search._build_search(REQUEST)
        self.assertTrue('site:' not in search_string,
                        'site: should not be in %s' % \
                        search_string)
        self.assertTrue('Errors:' not in info,
                        'Errors should not be printed '\
                        'if there are none')

    def testInvalidEngine(self):
        REQUEST = buildFakeRequest(self.search,
                                   'badEngine',
                                   'search string',
                                   'cdc.gov')
        self.assertRaises(EngineNotFoundException,
                          self.search._build_search, REQUEST)

    def testValidNoSearchString(self):
        REQUEST = buildFakeRequest(self.search,
                                   'google',
                                   '',
                                   'cdc.gov')
        info, search_string = self.search._build_search(REQUEST)
        self.assertEquals(search_string, '',
                          'A blank search string should '\
                          'return a blank string')

    def testValidCompleteSearch(self):
        REQUEST = buildFakeRequest(self.search,
                                   'google',
                                   'search this',
                                   'cdc.gov')
        search_safe = url_quote('site:cdc.gov search this')
        info, search_string = self.search._build_search(REQUEST)
        self.assertEquals(search_string,
                          'http://google.com/search?q=%s'\
                          % search_safe,
                          'This is a valid search and '\
                          'should return a valid search '\
                          'string')

class TestViewMethods(base.TypesTestCase):
    def afterSetUp(self):
        self.folder.invokeFactory('collective.types.ExternalSearch',
                                  'es')
        self.search = self.folder.es
        self.context = self.portal
        self.view = View(self.context, request=self.search.REQUEST)

class TestImage(base.TypesTestCase):
    """ExternalSearch image related tests
    """

    def testImage(self):
        """Trouble migrating images - make sure this type can handle
        a referenced image properly.
        """
        self.folder.invokeFactory('collective.types.ExternalSearch', id='imageTester')
        it = self.folder.imageTester
        self.folder.invokeFactory('Image', id='imageTest')
        img = self.folder.imageTest
        it.setImage(img)
        self.assertEquals(it.image.UID(), img.UID(), 
                          'referenced image UID is wrong')
        self.assertEquals(self.folder.imageTester.image.UID(), img.UID(), 
                          'referenced image UID is wrong')

    def testAnnotatable(self):
        """Resorting to shoving the name of the image in an annotation
        during the upgrade.  Make sure this works.
        """
        faux_image_name = 'pretty.png'
        self.folder.invokeFactory('collective.types.ExternalSearch',
                                  id='annotationTester')
        es = self.folder.annotationTester
        annotations = IAnnotations(es)
        annotations['image'] = faux_image_name

        self.assertEquals(faux_image_name, annotations[config.IMAGE_KEY])


class TestRunSearch(base.TypesFunctionalTestCase):
    """Run the search
    """

    def afterSetUp(self):
        self.folder.invokeFactory('collective.types.ExternalSearch',
                                  'es')
        self.search = self.folder.es
        self.portal.REQUEST.SESSION.id = 'testsession'

    def testBlankSearch(self):
        request = buildFakeRequest(self.portal,
                                   'google',
                                   '')
        self.search.context = self.search
        self.search.request = request
        result = self.search.execute_search()
        self.assertEquals(result, '',
                          'Blank search should not redirect')

    def testValidSearch1(self):
        request = buildFakeRequest(self.portal,
                                   'google',
                                   'blah')
        google = 'http://google.com/search?q=blah'
        self.search.context = self.search
        self.search.request = request
        result = self.search.execute_search()
        self.assertEquals(result, google,
                          'Google redirect not processed')

    def testValidSearch2(self):
        request = buildFakeRequest(self.portal,
                                   'google',
                                   'blah',
                                   'cdc.gov')
        self.search.context = self.search
        self.search.request = request
        google = 'http://google.com/search?q=' + \
                 url_quote('site:cdc.gov blah')
        result = self.search.execute_search()
        self.assertEquals(result, google,
                          'Google redirect not processed')
        
    
def test_suite():
    from unittest import TestSuite
    from unittest import makeSuite

    suite = TestSuite()
    suite.addTest(makeSuite(TestCreateExternalSearch))
    #suite.addTest(makeSuite(TestBuildSearch))
    suite.addTest(makeSuite(TestViewMethods))
    suite.addTest(makeSuite(TestImage))
    #suite.addTest(makeSuite(TestRunSearch))
    
    return suite

