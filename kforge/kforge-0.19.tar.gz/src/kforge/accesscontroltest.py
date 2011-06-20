import unittest
import kforge.accesscontrol
from kforge.testunit import TestCase
from kforge.exceptions import *

def suite():
    suites = [
        unittest.makeSuite(TestProjectAccessController),
    ]
    return unittest.TestSuite(suites)

class TestProjectAccessController(TestCase):
    
    def setUp(self):
        super(TestProjectAccessController, self).setUp()
        self.ac = kforge.accesscontrol.ProjectAccessController()
        self.person = None
        self.actionName = ''
        self.object = None
    
    def tearDown(self):
        self.ac = None

    def isAuthorised(self):
        return self.ac.isAuthorised(
            person=self.person, 
            actionName=self.actionName, 
            protectedObject=self.object, 
            project=self.registry.projects['administration'],
        )
    
    def test_setUp(self):
        self.failUnless(self.ac)

