import unittest
from kforge.exceptions import *
from kforge.dom.testunit import TestCase

def suite():
    suites = [
        unittest.makeSuite(TestMember),
    ]
    return unittest.TestSuite(suites)

class TestMember(TestCase):
    "TestCase for the Member class."
    
    def setUp(self):
        super(TestMember, self).setUp()
        try:
            self.person = self.registry.persons.create('TestMember')
        except:
            person = self.registry.persons['TestMember']
            person.delete()
            person.purge()
            raise
        try:
            self.project = self.registry.projects.create('TestMember')
        except:
            project = self.registry.projects['TestMember']
            project.delete()
            project.purge()
            self.person.delete()
            self.person = None
            raise
        else:
            try:
                member = self.project.members.create(self.person)
                self.member = member
            except:
                try:
                    member = self.project.members[self.person]
                    member.delete()
                    member.purge()
                except:
                    pass
                try:
                    self.project.delete()
                    self.project.purge()
                    self.project = None
                finally:
                    self.person.delete()
                    self.person.purge()
                    self.person = None
                raise

    def tearDown(self):
        try:
            self.member.delete()
            self.member.purge()
            self.member = None
        finally:
            try:
                self.project.delete()
                self.project.purge()
                self.project = None
            finally:
                self.person.delete()
                self.person.purge()
                self.person = None
    
    def test_new(self):
        self.failUnless(self.member, "New member could not be created.")
        # Suspended isUnique=True.         
        #self.failUnlessRaises(KforgeDomError,
        #    self.project.members.create, person=self.person
        #)
        self.failUnless(self.member.role,
            "New member has no role."
        )

    def test_find(self):
        self.failUnless(self.project.members.has_key(self.person),
            "New member could not be found."
        )

    def test_delete(self):
        self.member.delete()
        self.failUnlessRaises(KforgeRegistryKeyError,
            self.project.members.__getitem__, self.person
        )

    def test_is(self):
        self.failUnless(self.person in self.project.members,
            "New member doesn't appear to be there."
        )
        self.member.delete()
        self.failIf(self.person in self.project.members,
            "New member still appears to be there."
        )
