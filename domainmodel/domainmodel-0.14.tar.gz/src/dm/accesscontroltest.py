import unittest
import dm.accesscontrol
from dm.testunit import TestCase
from dm.exceptions import *

# Todo: Test for permissions set on a person's grants and bars.

def suite():
    suites = [
        unittest.makeSuite(TestSystemAccessController),
    ]
    return unittest.TestSuite(suites)

class TestSystemAccessController(TestCase):
    
    def setUp(self):
        super(TestSystemAccessController, self).setUp()
        self.ac = dm.accesscontrol.SystemAccessController()
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
        )
        
    def isPersonBarred(self):
        return self.ac.isPersonBarred(self.person)
    
    def test_setUp(self):
        self.failUnless(self.ac)

    def test_isAuthorised_nothing(self):
        self.failIf(self.isAuthorised())

    def test_isAuthorised_without_actionName_or_object(self):
        self.person = self.registry.persons['levin']
        self.failIf(self.isAuthorised())

    def test_isAuthorised_without_object(self):
        self.person = self.registry.persons['levin']
        self.actionName = 'Create'
        self.failIf(self.isAuthorised())

    def test_no_isAuthorised_delete_person(self):
        self.person = self.registry.persons['levin']
        self.actionName = 'Delete'
        self.object = self.registry.getDomainClass('Person')
        self.failIf(self.isAuthorised())

    def test_isAuthorised_read_person(self):
        self.person = self.registry.persons['levin']
        self.actionName = 'Read'
        self.object = self.registry.getDomainClass('Person')
        oldRole = self.person.role
        self.person.role = self.registry.roles['Administrator']
        self.failUnless(self.isAuthorised())
        self.person.role = oldRole

    def test_isAuthorised_visitor_create_person(self):
        self.person = self.registry.persons['visitor']
        self.actionName = 'Create'
        self.object = self.registry.getDomainClass('Person')
        self.ac.actionName = self.actionName
        self.ac.protectedObject = self.object
        self.failUnless(self.isAuthorised())

