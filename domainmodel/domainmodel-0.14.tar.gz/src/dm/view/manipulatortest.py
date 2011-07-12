import unittest
from dm.view.testunit import TestCase
from dm.view.manipulator import DomainObjectManipulator
from dm.view.manipulator import HasManyManipulator
from dm.ioc import *
from dm.util.datastructure import MultiValueDict

def suite():
    suites = [
        unittest.makeSuite(TestDomainObjectManipulator),
        unittest.makeSuite(TestDomainObjectManipulatorCreate),
        unittest.makeSuite(TestDomainObjectManipulatorUpdate),
        unittest.makeSuite(TestHasManyManipulator),
    ]
    return unittest.TestSuite(suites)

# Todo: Test for manipulator building fields for attr types: Text (ie Textarea), Integer, Date, Markdown, Url, Boolean, Image, default, and HasA when choices > 50. 

class ManipulatorTestCase(TestCase):

    def setUp(self):
        super(ManipulatorTestCase, self).setUp()
        self.manipulator = self.buildManipulator()

    def tearDown(self):
        self.manipulator = None
        super(ManipulatorTestCase, self).tearDown()
    
    def test_exists(self):
        self.failUnless(self.manipulator)
        self.failUnless(self.manipulator.fields)
    
    def buildManipulator(self):
        raise "Abstract method not implemented."


class DomainObjectManipulatorTestCase(ManipulatorTestCase):

    fixtureName = 'DomainObjectManipulatorTestCase'
    sessionKey = 'sessiontestkey34234234234535634561345'

    def setUp(self):
        super(DomainObjectManipulatorTestCase, self).setUp()
        self.validData = MultiValueDict()
        self.validData['name'] = self.fixtureName
        self.validData['fullname'] = 'DomainObject Manipulator TestCase'
        self.validData['password'] = 'password'
        self.validData['email'] = 'noreply@appropriatesoftware.net'
        self.validData['role'] = 'Visitor'
        self.validData['state'] = 'active'
        self.validData.setlist('memberships', ['administration', 'example'])
        self.invalidData = MultiValueDict()
        self.invalidData['wrong'] = 'wrong'
        self.sessionFixture = self.registry.sessions.create(self.sessionKey)

    def tearDown(self):
        super(DomainObjectManipulatorTestCase, self).tearDown()
        if self.sessionKey in self.registry.sessions:
            del(self.registry.sessions[self.sessionKey])
        if self.fixtureName in self.registry.persons.getAll():
            person = self.registry.persons.getAll()[self.fixtureName]
            person.delete()
            person.purge()

    def buildManipulator(self):
        return DomainObjectManipulator(objectRegister=self.registry.persons)


class TestDomainObjectManipulator(DomainObjectManipulatorTestCase):

    def testGetValidationErrors(self):
        errors = self.manipulator.getValidationErrors(self.validData)
        self.failIf(errors, str(errors))
        errors = self.manipulator.getValidationErrors(self.invalidData)
        self.failUnless(errors, str(errors))

    def testDecodeHtml(self):
        self.manipulator.decodeHtml(self.validData)


class TestDomainObjectManipulatorCreate(DomainObjectManipulatorTestCase):

    def setUp(self):
        super(TestDomainObjectManipulatorCreate, self).setUp()
        self.manipulator.create(self.validData)

    def testCreate(self):
        person = self.registry.persons[self.fixtureName]
        self.failUnlessEqual(person.name, self.validData['name'])
        self.failUnlessEqual(person.fullname, self.validData['fullname'])
        self.failUnlessEqual(person.email, self.validData['email'])
        self.failUnlessEqual(person.role.getRegisterKeyValue(), self.validData['role'])
        self.sessionFixture.person = person
        self.sessionFixture.save()
        self.failUnless(self.sessionKey in person.sessions)


class TestDomainObjectManipulatorUpdate(DomainObjectManipulatorTestCase):

    def setUp(self):
        super(TestDomainObjectManipulatorUpdate, self).setUp()
        self.manipulator.create(self.validData)
        objectRegister = self.registry.persons
        domainObject = self.manipulator.domainObject
        self.manipulator = None
        self.manipulator = DomainObjectManipulator(
            objectRegister=objectRegister,
            domainObject=domainObject,
        )
        
    def testUpdateString(self):
        self.validData['fullname'] = 'Update ' + self.validData['fullname']
        self.manipulator.update(self.validData)
        person = self.registry.persons[self.fixtureName]
        self.failUnlessEqual(person.fullname, self.validData['fullname'])

    def testUpdateHasA(self):
        self.validData['role'] = 'Developer'
        self.manipulator.update(self.validData)
        person = self.registry.persons[self.fixtureName]
        self.failUnlessEqual(person.role.getRegisterKeyValue(), self.validData['role'])

    def testUpdateHasMany(self):
        person = self.registry.persons[self.fixtureName]
        self.failIf(self.sessionKey in person.sessions)
        self.sessionFixture.person = person
        self.sessionFixture.save()
        self.failUnless(self.sessionKey in person.sessions)
        self.validData.setlist('sessions', [''])
        self.manipulator.update(self.validData)
        self.failIf(self.sessionKey in person.sessions)


class HasManyManipulatorTestCase(ManipulatorTestCase):

    sessionKey = 'sessiontestkey34234234234535634561345'
    personName = 'levin'
    roleName = 'Developer'

    def setUp(self):
        self.person = self.registry.persons[self.personName]
        super(HasManyManipulatorTestCase, self).setUp()
        self.validData = MultiValueDict()
        self.validData['person'] = self.personName
        self.validData['key'] = self.sessionKey
        self.validData['lastVisited'] = ''
        self.invalidData = MultiValueDict()
        self.invalidData['person'] = self.personName
        self.invalidData['key'] = self.sessionKey
        self.invalidData['lastVisited'] = 'letters'
        self.sessionFixture = self.registry.sessions.create(self.sessionKey)

    def tearDown(self):
        super(HasManyManipulatorTestCase, self).tearDown()
        if self.sessionKey in self.registry.sessions:
            del(self.registry.sessions[self.sessionKey])

    def buildManipulator(self):
        return HasManyManipulator(objectRegister=self.person.sessions)


class TestHasManyManipulator(HasManyManipulatorTestCase):

    def testGetValidationErrors(self):
        errors = self.manipulator.getValidationErrors(self.validData)
        self.failIf(errors, str(errors))
        errors = self.manipulator.getValidationErrors(self.invalidData)
        self.failUnless(errors, str(errors))

    def testDecodeHtml(self):
        self.manipulator.decodeHtml(self.validData)

    def testCreate(self):
        self.manipulator.create(self.validData)

