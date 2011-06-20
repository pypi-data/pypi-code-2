import unittest
from kforge.exceptions import *
from kforge.dom.testunit import TestCase

def suite():
    suites = [
        unittest.makeSuite(TestPendingMember),
    ]
    return unittest.TestSuite(suites)

class TestPendingMember(TestCase):
    "TestCase for the PendingMember class."
    
    def setUp(self):
        super(TestPendingMember, self).setUp()
        try:
            self.person = self.registry.persons.create('TestPendingMember')
        except:
            person = self.registry.persons['TestPendingMember']
            person.delete()
            person.purge()
            raise
        try:
            self.project = self.registry.projects.create('TestPendingMember')
        except:
            project = self.registry.projects['TestPendingMember']
            project.delete()
            project.purge()
            self.person.delete()
            self.person = None
            raise
        else:
            try:
                member = self.project.pending_members.create(self.person)
                self.member = member
            except:
                try:
                    member = self.project.pending_members[self.person]
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

    def test_find(self):
        self.failUnless(self.project.pending_members.has_key(self.person),
            "New member could not be found."
        )

    def test_delete(self):
        self.member.delete()
        self.failUnlessRaises(KforgeRegistryKeyError,
            self.project.pending_members.__getitem__, self.person
        )

    def test_is(self):
        self.failUnless(self.person in self.project.pending_members,
            "New member doesn't appear to be there."
        )
        self.member.delete()
        self.failIf(self.person in self.project.pending_members,
            "New member still appears to be there."
        )
