import kforge.dom.projecttest
import kforge.dom.membertest
import kforge.dom.servicetest
import kforge.dom.feedentrytest
from kforge.dom.testunit import TestCase
from kforge.exceptions import *
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestDomainRegistry),
        unittest.makeSuite(TestPluginNotification),
        kforge.dom.projecttest.suite(),
        kforge.dom.membertest.suite(),
        kforge.dom.servicetest.suite(),
        kforge.dom.feedentrytest.suite(),
    ]
    return unittest.TestSuite(suites)


class TestDomainRegistry(TestCase):
    "TestCase for the DomainRegistry class."

    def setUp(self):
        super(TestDomainRegistry, self).setUp()
        
    def tearDown(self):
        projects = self.registry.projects
        try:
            project = projects['TestDomainRegistry']
            project.delete()
            project.purge()
        except:
            pass
        persons = self.registry.persons
        try:
            person = persons['TestDomainRegistry']
            person.delete()
            person.purge()
        except:
            pass

    def testExists(self):
        self.registry

    def test_project(self):
        projects = self.registry.projects
        project = projects.create('TestDomainRegistry')

        self.failUnless(project.id, "No project id set.")
        try:
            self.failUnless(project, "No project created.")
            self.failUnless(projects['TestDomainRegistry'], "No project found.")
            self.failIf('TestDomainRegistry2' in projects, "Project found.")
            try:
                projects['TestDomainRegistry2']
            except KforgeRegistryKeyError:
                pass
            else:
                self.fail("Strange project found.")
        finally:
            project.delete()
            project.purge()

    def test_person(self):
        persons = self.registry.persons
        person = persons.create('TestDomainRegistry')
        try:
            self.failUnless(person, "No person created.")
            self.failUnless(persons['TestDomainRegistry'], "No person found.")
            self.failIf(persons.has_key('TestDomainRegistry2'), "Person found.")
            try:
                persons['TestDomainRegistry2']
            except KforgeRegistryKeyError:
                pass
            else:
                self.fail("Strange person found.")
        finally:
            person.delete()
            person.purge()

    def test_plugin(self):
        plugins = self.registry.plugins
        try:
            plugin = plugins.create('testingexample')
        except:
            plugin = plugins['testingexample']
            plugin.delete()
            raise
            
        try:
            self.failUnless(plugin, "No plugin created.")
            self.failUnless(plugin.getSystem(), "Domain object has no system.")
            self.failUnless(plugins['testingexample'], "No plugin found.")
            self.failIf(plugins.has_key('notaplugin'), "Plugin found.")
            try:
                plugins['notaplugin']
            except KforgeRegistryKeyError:
                pass
            else:
                self.fail("Strange plugin found.")
        finally:
            plugin.delete()

    def test_service(self):
        registry = self.registry.services

    def test_member(self):
        registry = self.registry.members
    
    def testMember(self):
        self.project = self.registry.projects.create('TestDomainRegistry')
        try:
            self.person  = self.registry.persons.create('TestDomainRegistry')
            self.person2 = self.registry.persons.create('TestDomainRegistry2')
        except:
            self.project.delete()
            self.project.purge()
            raise

        member = self.project.members.create(person=self.person)
        try:
            self.failUnless(member, "No member created.")
            foundMember = self.project.members[self.person]
            self.failUnless(foundMember, "No member found.")
            isMember = self.project.members.has_key(self.person2)
            self.failIf(isMember, "Strange member found.")
        finally:
            try:
                member.delete()
                member.purge()
            finally:
                try:
                    self.person2.delete()
                    self.person2.purge()
                    self.person.delete()
                    self.person.purge()
                finally:
                    self.project.delete()
                    self.project.purge()

class TestPluginNotification(TestCase):
    "TestCase for the Person class."
    
    def setUp(self):
        super(TestPluginNotification, self).setUp()
        self.fixtureName = 'TestPluginNotification'
        self.persons = self.registry.persons

    def tearDown(self):
        try:
            person = self.persons[self.fixtureName]
            person.delete()
            person.purge()
        except:
            pass

        self.person = None
  
    def test_counts(self):
        self.examplePlugin = self.registry.plugins['example']

        before = self.examplePlugin.getSystem().counts['onPersonCreate']
        self.person = self.persons.create(self.fixtureName)
        after = self.examplePlugin.getSystem().counts['onPersonCreate']
        self.failUnless(before + 1 == after)
        
        before = self.examplePlugin.getSystem().counts['onPersonDelete']
        self.person.delete()
        after = self.examplePlugin.getSystem().counts['onPersonDelete']
        self.failUnless(before + 1 == after)
        
        before = self.examplePlugin.getSystem().counts['onPersonUndelete']
        self.person.undelete()
        after = self.examplePlugin.getSystem().counts['onPersonUndelete']
        self.failUnless(before + 1 == after)
        
        before = self.examplePlugin.getSystem().counts['onPersonDelete']
        self.person.delete()
        after = self.examplePlugin.getSystem().counts['onPersonDelete']
        self.failUnless(before + 1 == after)
        
        before = self.examplePlugin.getSystem().counts['onPersonPurge']
        self.person.purge()
        after = self.examplePlugin.getSystem().counts['onPersonPurge']
        self.failUnless(before + 1 == after)
