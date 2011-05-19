from inqbus.folderlistings.tests.base import FolderlistingsTestCase
from inqbus.folderlistings.browser.inqbus_folderlistings import Folderlisting

from Products.Five.browser import BrowserView

import unittest

class TestSetup(FolderlistingsTestCase):
    """
    """
    
    def afterSetUp(self):
        """
        """
        
    def beforeTearDown(self):
        """
        """
        
    def test_create_folderlisting_instance(self):
        """ a function to test the __init__ method
        """
        self.folderlisting = Folderlisting(self.portal, self.portal.REQUEST)
        if self.folderlisting:
            test = True
        else:
            test = False
        self.failUnless(test)
        # If we dont set anythin in the request, he should use the default values.
        # Lets check it!
        # The sort_on should be 'modified' ...
        self.assertEqual(self.folderlisting.sort_on, 'modified')
        # ... and the sort_order 'descending'
        self.assertEqual(self.folderlisting.sort_on, 'modified')
        # Lets try to set the different sort_ons ...
        # Sort on title
        title_request = self.portal.REQUEST
        title_request['sort_on'] = 'sortable_title'
        self.folderlisting.__init__(self.portal, title_request)
        self.assertEqual(self.folderlisting.sort_on, 'sortable_title')
        # Sort on author
        author_request = self.portal.REQUEST
        author_request['sort_on'] = 'Creator'
        self.folderlisting.__init__(self.portal, author_request)
        self.assertEqual(self.folderlisting.sort_on, 'Creator')
        # Sort on type
        type_request = self.portal.REQUEST
        type_request['sort_on'] = 'portal_type'
        self.folderlisting.__init__(self.portal, type_request)
        self.assertEqual(self.folderlisting.sort_on, 'portal_type')
        
def test_suite():
    """
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite