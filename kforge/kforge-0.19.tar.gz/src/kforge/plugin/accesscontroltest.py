from kforge.testunit import TestCase
import unittest
import kforge.command
import kforge.plugin.accesscontrol

def suite():
    suites = [
            unittest.makeSuite(TestPlugin),
        ]
    return unittest.TestSuite(suites)


class TestPlugin(TestCase):
    """
    TestCase for the access control plugin.
    """

    def setUp(self):
        super(TestPlugin, self).setUp()
        domainObject = type('Plugin', (), {})
        domainObject.name = 'accesscontrol'
        self.plugin = kforge.plugin.accesscontrol.Plugin(domainObject)
        self.fixtureName = 'TestAccessControlPlugin'
        if self.fixtureName in self.registry.persons:
            person = self.registry.persons[self.fixtureName]
            person.delete()
            person.purge()
        self.person = self.registry.persons.create(self.fixtureName)
        for grant in self.person.grants:
            grant.delete()

    def tearDown(self):
        self.command = None
        self.plugin = None
        if self.fixtureName in self.registry.persons:
            person = self.registry.persons[self.fixtureName]
            person.delete()
            person.purge()
            person = None

    def test_pluginSystemExists(self):
        self.failUnless(self.plugin)

    def test_onCreatePerson(self):
        self.failIf(len(self.person.grants.keys()),
            "There are grants: %s" % len(self.person.grants.keys()))
        self.plugin.onPersonCreate(self.person)
        self.failUnless(len(self.person.grants.keys()),
            "There are no grants: %s" % self.person.grants.keys())

        
