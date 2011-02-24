import unittest
from provide.dom.testunit import TestCase
from provide.locator import PurposeLocator
from provide.locator import PathPurposeLocator
from provide.locator import DomainPurposeLocator
from provide.dictionarywords import DOMAIN_NAME

def suite():
    suites = [
        unittest.makeSuite(TestPurposeLocator),
        unittest.makeSuite(TestPathPurposeLocator),
        unittest.makeSuite(TestDomainPurposeLocator),
    ]
    return unittest.TestSuite(suites)


class TestPurposeLocator(TestCase):

    locatorClass = PurposeLocator
    domainName = 'provide.example.domain'
    provisionName = 'scanbooker'
    purposeName1 = 'production'
    purposeName2 = 'test'
    purposeName3 = 'accept'
    requiredDistinguishesDomains = True
    requiredFqdn1 = 'scanbooker.example.domain'
    requiredFqdn2 = 'scanbooker.example.domain'
    requiredFqdn3 = 'scanbooker.example.domain'
    requiredPath1 = ''
    requiredPath2 = '/test'
    requiredPath3 = '/accept'

    def setUp(self):
        super(TestPurposeLocator, self).setUp()
        self.dictionary.set(DOMAIN_NAME, self.domainName)
        self.provision = self.registry.provisions.create(self.provisionName)
        self.purpose1 = self.provision.purposes.create(self.purposeName1)
        self.purpose2 = self.provision.purposes.create(self.purposeName2)
        self.purpose3 = self.provision.purposes.create(self.purposeName3)
        self.locator = self.createPurposeLocator()

    def createPurposeLocator(self):
        return self.locatorClass()

    def tearDown(self):
        super(TestPurposeLocator, self).tearDown()
        if self.provisionName in self.registry.provisions:
            provision = self.registry.provisions[self.provisionName]
            provision.delete()

    def test_locator(self):
        self.failUnlessEqual(self.locator.__class__, self.locatorClass)
        self.failUnlessEqual(
            self.locator.distinguishesDomains(),
            self.requiredDistinguishesDomains
        )
        self.failUnlessFqdn()
        self.failUnlessPath()

    def failUnlessFqdn(self):
        fqdn = self.locator.getFQDN(self.purpose1)
        self.failUnlessEqual(fqdn, self.requiredFqdn1)
        fqdn = self.locator.getFQDN(self.purpose2)
        self.failUnlessEqual(fqdn, self.requiredFqdn2)
        fqdn = self.locator.getFQDN(self.purpose3)
        self.failUnlessEqual(fqdn, self.requiredFqdn3)

    def failUnlessPath(self):
        fqdn = self.locator.getPath(self.purpose1)
        self.failUnlessEqual(fqdn, self.requiredPath1)
        fqdn = self.locator.getPath(self.purpose2)
        self.failUnlessEqual(fqdn, self.requiredPath2)
        fqdn = self.locator.getPath(self.purpose3)
        self.failUnlessEqual(fqdn, self.requiredPath3)


class TestPathPurposeLocator(TestPurposeLocator):

    locatorClass = PathPurposeLocator
    requiredDistinguishesDomains = False
    requiredFqdn1 = 'provide.example.domain'
    requiredFqdn2 = 'provide.example.domain'
    requiredFqdn3 = 'provide.example.domain'
    requiredPath1 = '/scanbooker'
    requiredPath2 = '/test/scanbooker'
    requiredPath3 = '/accept/scanbooker'


class TestDomainPurposeLocator(TestPurposeLocator):

    locatorClass = DomainPurposeLocator
    requiredFqdn1 = 'scanbooker.example.domain'
    requiredFqdn2 = 'scanbooker.test.example.domain'
    requiredFqdn3 = 'scanbooker.accept.example.domain'
    requiredPath1 = ''
    requiredPath2 = ''
    requiredPath3 = ''

