import unittest
from kforge.django.apps.kui.views.testunit import TestCase
from dm import webkit
if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
    from kforge.django.apps.kui.views.manipulator import PasswordField
    from kforge.django.apps.kui.views.manipulator import ProjectNameField
    from kforge.django.apps.kui.views.manipulator import PersonNameField
    from kforge.django.apps.kui.views.manipulator import ServiceNameField
from kforge.django.apps.kui.views.manipulator import PersonCreateManipulator
from kforge.django.apps.kui.views.manipulator import PersonUpdateManipulator
from kforge.django.apps.kui.views.manipulator import ProjectCreateManipulator
from kforge.django.apps.kui.views.manipulator import ProjectUpdateManipulator
from kforge.django.apps.kui.views.manipulator import ServiceCreateManipulator
from kforge.django.apps.kui.views.manipulator import ServiceUpdateManipulator
from kforge.django.apps.kui.views.manipulator import DomainObjectManipulator
from kforge.django.apps.kui.views.manipulator import HasManyManipulator
from django.utils.datastructures import MultiValueDict
from kforge.ioc import *

def suite():
    suites = [
        unittest.makeSuite(TestPersonCreateManipulator),
        unittest.makeSuite(TestPersonUpdateManipulator),
        unittest.makeSuite(TestProjectCreateManipulator),
        unittest.makeSuite(TestProjectUpdateManipulator),
        unittest.makeSuite(TestServiceCreateManipulator),
        unittest.makeSuite(TestServiceUpdateManipulator),
        # Todo: Move these to dm.
        unittest.makeSuite(TestDomainObjectManipulator),
        unittest.makeSuite(TestDomainObjectManipulatorCreate),
        unittest.makeSuite(TestDomainObjectManipulatorUpdate),
        unittest.makeSuite(TestHasManyManipulator),
    ]
    if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':
        suites = [
            unittest.makeSuite(TestPasswordField),
            unittest.makeSuite(TestPersonNameField),
            unittest.makeSuite(TestProjectNameField),
            unittest.makeSuite(TestServiceNameField),
        ] + suites
    suites = [
        unittest.makeSuite(TestDomainObjectManipulator),
        unittest.makeSuite(TestHasManyManipulator),
    ]
    return unittest.TestSuite(suites)


if webkit.webkitName == 'django' and webkit.webkitVersion == '1.0':

    class FieldTestCase(TestCase):

        fieldClass = None
        fieldValids = []
        fieldInvalids = []

        def setUp(self):
            self.field = self.fieldClass()

        def tearDown(self):
            self.field = None

        def testField(self):
            for v in self.fieldValids:
                try:
                    self.field.clean(v)
                except webkit.ValidationError, inst:
                    self.fail("Should be valid: %s %s %s" % (v, self.field, inst)) 
            for v in self.fieldInvalids:
                try:
                    self.field.clean(v)
                except webkit.ValidationError:
                    pass
                else:
                    self.fail("Should be invalid: %s %s" % (v, self.field)) 


    class TestPasswordField(FieldTestCase):
        
        fieldClass = PasswordField
        fieldValids = ['meme']
        fieldInvalids = ['', 'm', 'me', 'mem']
       

    class TestPersonNameField(FieldTestCase):
        
        fieldClass = PersonNameField
        fieldValids = ['..', 'jo', 'joh', 'john', 'john99', 'johnbywater', 'john-bywater', 'john.bywater', 'john_bywater', 'johnbywaterrrrrrrrrr']
        fieldInvalids = ['', '.', '', 'm', '1', ' ', 'home', 'create', 'find', 'search', 'update', 'delete', 'purge', 'login', 'logout', 'johnbywaterrrrrrrrrrrz']

       
    class TestProjectNameField(FieldTestCase):
        
        fieldClass = ProjectNameField
        fieldValids = ['mem', 'meme', 'mem99' ]
        fieldInvalids = ['', 'm', 'me', 'meme.', 'meme-', 'meme_', 'home' ,'create' ,'find' ,'search' ,'update' ,'delete' ,'purge' ,'admin' ,'person' ,'project' ,'login' ,'media', 'sixteencharsssss']


    class TestServiceNameField(FieldTestCase):
        
        fieldClass = ServiceNameField
        fieldValids = ['m', 'me', 'mem', 'meme', 'mem99', 'Mem']
        fieldInvalids = ['', '%', '$', '/', '&', 'seventeencharssss']


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


class PersonManipulatorTestCase(ManipulatorTestCase):

    fixtureName = 'PersonManipulatorTestCase'

    def setUp(self):
        super(PersonManipulatorTestCase, self).setUp()
        self.tearDownFixtures()
        self.validData = MultiValueDict()
        self.validData['name'] = self.fixtureName
        self.invalidData = MultiValueDict()
        self.invalidData['name'] = '%%'

    def tearDown(self):
        super(PersonManipulatorTestCase, self).tearDown()
        self.tearDownFixtures()
        
    def tearDownFixtures(self):
        if self.fixtureName in self.registry.persons.getAll():
            person = self.registry.persons.getAll()[self.fixtureName]
            person.delete()
            person.purge()


class TestPersonCreateManipulator(PersonManipulatorTestCase):

    def setUp(self):
        super(TestPersonCreateManipulator, self).setUp()
        self.manipulator.create(self.validData)

    def testCreate(self):
        person = self.registry.persons[self.fixtureName]
        self.failUnlessEqual(person.name, self.validData['name'])
    
    def buildManipulator(self):
        return PersonCreateManipulator(objectRegister=self.registry.persons)


class TestPersonUpdateManipulator(PersonManipulatorTestCase):

    def setUp(self):
        super(TestPersonUpdateManipulator, self).setUp()
        self.manipulator.create(self.validData)

    def testUpdate(self):
        person = self.registry.persons[self.fixtureName]
        self.failUnlessEqual(person.name, self.validData['name'])
        self.validData['email'] = 'john@doe.com'
        self.manipulator.update(self.validData)
        person = self.registry.persons[self.fixtureName]
        self.failUnlessEqual(person.email, self.validData['email'])

    def buildManipulator(self):
        return PersonUpdateManipulator(objectRegister=self.registry.persons)


class ProjectManipulatorTestCase(ManipulatorTestCase):

    fixtureName = 'ProjectManipulatorTestCase'
    fixtureDescription = 'Project manipulator test case.'

    def setUp(self):
        super(ProjectManipulatorTestCase, self).setUp()
        self.tearDownFixtures()
        self.validData = MultiValueDict()
        self.validData['name'] = self.fixtureName
        self.validData['description'] = self.fixtureDescription
        self.invalidData = MultiValueDict()
        self.invalidData['wrong'] = 'wrong'

    def tearDown(self):
        super(ProjectManipulatorTestCase, self).tearDown()
        self.tearDownFixtures()

    def tearDownFixtures(self):
        if self.fixtureName in self.registry.projects.getAll():
            project = self.registry.projects.getAll()[self.fixtureName]
            project.delete()
            project.purge()


class TestProjectCreateManipulator(ProjectManipulatorTestCase):

    def setUp(self):
        super(TestProjectCreateManipulator, self).setUp()
        self.manipulator.create(self.validData)

    def testCreate(self):
        project = self.registry.projects[self.fixtureName]
        self.failUnlessEqual(project.name, self.validData['name'])
    
    def buildManipulator(self):
        return ProjectCreateManipulator(objectRegister=self.registry.projects)


class TestProjectUpdateManipulator(ProjectManipulatorTestCase):

    def setUp(self):
        super(TestProjectUpdateManipulator, self).setUp()
        self.manipulator.create(self.validData)

    def testUpdate(self):
        project = self.registry.projects[self.fixtureName]
        self.failUnlessEqual(project.name, self.validData['name'])
        self.validData['description'] = 'Blah blah blah'
        self.manipulator.update(self.validData)
        project = self.registry.projects[self.fixtureName]
        self.failUnlessEqual(project.description, self.validData['description'])

    def buildManipulator(self):
        return ProjectUpdateManipulator(objectRegister=self.registry.projects)


class ServiceManipulatorTestCase(ManipulatorTestCase):

    fixtureName = 'ServiceManipulatorTestCase'
    pluginFixtureName = 'example'
    projectFixtureName = 'ServiceManipulatorTestCase'

    def setUp(self):
        super(ServiceManipulatorTestCase, self).setUp()
        self.tearDownFixtures()
        self.projectData = MultiValueDict()
        self.projectData['name'] = self.projectFixtureName
        self.pluginFixture = self.registry.plugins[self.pluginFixtureName]
        projectsManipulator = ProjectCreateManipulator(objectRegister=self.registry.projects)
        projectsManipulator.create(self.projectData)
        self.projectFixture = self.registry.projects[self.projectFixtureName]
        self.validData = MultiValueDict()
        self.validData['name'] = self.fixtureName
        self.validData['project'] = self.projectFixtureName
        self.validData['plugin'] = self.pluginFixtureName
        self.invalidData = MultiValueDict()
        self.invalidData['wrong'] = 'wrong'

    def tearDown(self):
        super(ServiceManipulatorTestCase, self).tearDown()
        self.tearDownFixtures()

    def tearDownFixtures(self):
        if self.fixtureName in self.registry.projects.getAll():
            project = self.registry.projects.getAll()[self.fixtureName]
            project.delete()
            project.purge()


class TestServiceCreateManipulator(ServiceManipulatorTestCase):

    def setUp(self):
        super(TestServiceCreateManipulator, self).setUp()
        self.manipulator.create(self.validData)

    def testCreate(self):
        service = self.projectFixture.services[self.fixtureName]
        self.failUnlessEqual(service.name, self.validData['name'])
    
    def buildManipulator(self):
        return ServiceCreateManipulator(objectRegister=self.registry.services)


class TestServiceUpdateManipulator(ServiceManipulatorTestCase):

    def setUp(self):
        super(TestServiceUpdateManipulator, self).setUp()
        self.manipulator.create(self.validData)

    def testUpdate(self):
        service = self.projectFixture.services[self.fixtureName]
        self.failUnlessEqual(service.name, self.validData['name'])
        newName = 'Blah blah blah'
        self.validData['name'] = newName
        self.manipulator.update(self.validData)
        service = self.projectFixture.services[newName]
        self.failUnlessEqual(service.name, newName) 
        self.failUnlessEqual(service.plugin.name, self.validData['plugin'])

    def buildManipulator(self):
        return ServiceUpdateManipulator(objectRegister=self.registry.services)


class DomainObjectManipulatorTestCase(ManipulatorTestCase):

    fixtureName = 'DomainObjectManipulatorTestCase'

    def setUp(self):
        super(DomainObjectManipulatorTestCase, self).setUp()
        self.validData = MultiValueDict()
        self.validData['name'] = self.fixtureName
        self.validData['fullname'] = 'DomainObject Manipulator TestCase'
        self.validData['password'] = 'password'
        self.validData['email'] = 'email@email.com'
        self.validData['role'] = 'Visitor'
        self.validData['state'] = 'active'
        self.validData.setlist('memberships', ['administration', 'example'])
        self.invalidData = MultiValueDict()
        self.invalidData['name'] = self.fixtureName
        self.invalidData['fullname'] = 'DomainObject Manipulator TestCase'
        self.invalidData['password'] = 'password'
        self.invalidData['email'] = 'email@email.com'
        self.invalidData['role'] = 'Destroyer'
        self.invalidData['state'] = 'active'

    def tearDown(self):
        super(DomainObjectManipulatorTestCase, self).tearDown()
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
        adminProject = self.registry.projects['administration']
        self.failUnless(adminProject in person.memberships)


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
        self.validData.setlist('memberships', ['example'])
        self.manipulator.update(self.validData)
        person = self.registry.persons[self.fixtureName]
        adminProject = self.registry.projects['administration']
        self.failIf(adminProject in person.memberships)


class HasManyManipulatorTestCase(ManipulatorTestCase):

    projectName = 'warandpeace'
    personName = 'levin'
    roleName = 'Developer'

    def setUp(self):
        super(HasManyManipulatorTestCase, self).setUp()
        self.person = self.registry.persons[self.personName]
        self.validData = MultiValueDict()
        self.validData['person'] = self.personName
        self.validData['role'] = self.roleName
        self.invalidData = MultiValueDict()
        self.invalidData['person'] = self.personName
        self.invalidData['role'] = 'Destroyer'

    def tearDown(self):
        super(HasManyManipulatorTestCase, self).tearDown()
        if self.person in self.project.members:
            membership = self.project.members[self.person]
            membership.delete()
            membership.purge()

    def buildManipulator(self):
        self.project = self.registry.projects[self.projectName]
        return HasManyManipulator(objectRegister=self.project.members)


class TestHasManyManipulator(HasManyManipulatorTestCase):

    def testGetValidationErrors(self):
        errors = self.manipulator.getValidationErrors(self.validData)
        self.failIf(errors, str(errors))
        errors = self.manipulator.getValidationErrors(self.invalidData)
        self.failUnless(errors, str(errors))

    def testDecodeHtml(self):
        self.manipulator.decodeHtml(self.validData)

