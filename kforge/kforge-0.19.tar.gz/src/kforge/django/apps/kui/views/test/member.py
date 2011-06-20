import unittest
from kforge.django.apps.kui.views.test.base import ViewTestCase
from kforge.django.apps.kui.views.member import MemberListView
from kforge.django.apps.kui.views.member import MemberCreateView
from kforge.django.apps.kui.views.member import MemberUpdateView
from kforge.django.apps.kui.views.member import MemberDeleteView
import kforge.ioc
from dm.util.datastructure import MultiValueDict

def suite():
    suites = [
        unittest.makeSuite(TestMemberListView),
        unittest.makeSuite(TestMemberCreateView),
        unittest.makeSuite(TestMemberCreateViewLevin),
        unittest.makeSuite(TestMemberCreateViewLevinPOST),
        unittest.makeSuite(TestMemberCreateViewLevinPOSTErrorNoRole),
        unittest.makeSuite(TestMemberCreateViewLevinPOSTErrorNoPerson),
        unittest.makeSuite(TestMemberCreateViewLevinPOSTErrorAlreadyMember),
        unittest.makeSuite(TestMemberUpdateView),
        unittest.makeSuite(TestMemberUpdateViewLevin),
        unittest.makeSuite(TestMemberUpdateViewLevinPOST),
        unittest.makeSuite(TestMemberDeleteView),
        unittest.makeSuite(TestMemberDeleteViewLevin),
        unittest.makeSuite(TestMemberDeleteViewLevinPOST),
        unittest.makeSuite(TestMemberDeleteViewAdministrator),
        unittest.makeSuite(TestMemberDeleteViewAdministratorPOST),
        unittest.makeSuite(TestMemberDeleteViewNatasha),
        unittest.makeSuite(TestMemberDeleteViewNatashaPOST),
    ]
    return unittest.TestSuite(suites)


class MemberViewTestCase(ViewTestCase):

    sysdict = kforge.ioc.RequiredFeature('SystemDictionary')
    projectName = 'administration'
    requiredRedirect = '%s/login/' % ViewTestCase.URI_PREFIX
    requiredResponseClassName = 'HttpResponseRedirect'

    def createViewKwds(self):
        viewKwds = super(MemberViewTestCase, self).createViewKwds()
        viewKwds['domainObjectKey'] = self.projectName
        if hasattr(self, 'personName'):
            viewKwds['hasManyKey'] = self.personName
        return viewKwds
    
    def test_canAccess(self):
        self.failIf(self.view.canAccess())


class TestMemberListView(MemberViewTestCase):

    viewClass = MemberListView
    requiredRedirect = ''
    requiredResponseClassName = 'HttpResponse'

    def test_canAccess(self):
        self.failUnless(self.view.canAccess())


class TestMemberCreateView(MemberViewTestCase):

    projectName = 'annakarenina'
    viewClass = MemberCreateView
        
    def test_canAccess(self):
        self.failIf(self.view.canAccess())


class TestMemberCreateViewLevin(MemberViewTestCase):

    viewerName = 'levin'
    projectName = 'annakarenina'
    viewClass = MemberCreateView
    requiredResponseClassName = 'HttpResponse'
    requiredRedirect = ''
        
    def test_canAccess(self):
        self.failUnless(self.view.canAccess())


class TestMemberCreateViewLevinPOST(MemberViewTestCase):

    viewerName = 'levin'
    projectName = 'annakarenina'
    viewClass = MemberCreateView
    POST = MultiValueDict({'person': ['visitor'], 'role': ['Developer']})
    requiredFormErrors = False
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/project/annakarenina/members/'
        
    def test_canAccess(self):
        self.failUnless(self.view.canAccess())

    def tearDown(self):
        super(TestMemberCreateViewLevinPOST, self).tearDown()
        person = self.registry.persons['visitor']
        if person in self.registry.projects[self.projectName].members:
            o = self.registry.projects[self.projectName].members[person]
            o.delete()
            o.purge()

class TestMemberCreateViewLevinPOSTErrorNoRole(MemberViewTestCase):

    viewerName = 'levin'
    projectName = 'annakarenina'
    viewClass = MemberCreateView
    POST = MultiValueDict({'person': ['natasha']})
    requiredFormErrors = ['role', 'is required']
    requiredResponseClassName = 'HttpResponseBadRequest'
    requiredRedirect = ''
        
    def test_canAccess(self):
        self.failUnless(self.view.canAccess())


class TestMemberCreateViewLevinPOSTErrorNoPerson(MemberViewTestCase):

    viewerName = 'levin'
    projectName = 'annakarenina'
    viewClass = MemberCreateView
    POST = MultiValueDict({'role': ['Administrator']})
    requiredFormErrors = ['person', 'is required']
    requiredResponseClassName = 'HttpResponseBadRequest'
    requiredRedirect = ''
        
    def test_canAccess(self):
        self.failUnless(self.view.canAccess())


class TestMemberCreateViewLevinPOSTErrorAlreadyMember(MemberViewTestCase):

    viewerName = 'levin'
    projectName = 'annakarenina'
    viewClass = MemberCreateView
    POST = MultiValueDict({'person': ['levin'], 'role': ['Developer']})
    requiredFormErrors = ['is already a member of this project']
    requiredResponseClassName = 'HttpResponseBadRequest'
    requiredRedirect = ''
        
    def test_canAccess(self):
        self.failUnless(self.view.canAccess())


class TestMemberUpdateView(MemberViewTestCase):

    viewerName = 'natasha'
    viewClass = MemberUpdateView
    projectName = 'annakarenina'
    personName = 'levin'
    requiredRedirect = '/accessDenied/'
    
    def test_canAccess(self):
        self.failIf(self.view.canAccess())


class TestMemberUpdateViewLevin(MemberViewTestCase):

    viewerName = 'levin'
    viewClass = MemberUpdateView
    projectName = 'annakarenina'
    personName = 'levin'
    requiredRedirect = ''
    requiredResponseClassName = 'HttpResponse'
    
    def test_canAccess(self):
        self.failUnless(self.view.canAccess())


class TestMemberUpdateViewLevinPOST(MemberViewTestCase):

    viewerName = 'levin'
    projectName = 'annakarenina'
    personName = 'visitor'
    viewClass = MemberUpdateView
    POST = MultiValueDict({'person': ['visitor'], 'role': ['Developer']})
    requiredFormErrors = False
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/project/annakarenina/members/'
    
    def setUp(self):
        super(TestMemberUpdateViewLevinPOST, self).setUp()
        person = self.registry.persons['visitor']
        role = self.registry.roles['Friend']
        self.registry.projects[self.projectName].members.create(person, role=role)
    
    def tearDown(self):
        super(TestMemberUpdateViewLevinPOST, self).tearDown()
        person = self.registry.persons['visitor']
        if person in self.registry.projects[self.projectName].members:
            member = self.registry.projects[self.projectName].members[person]
            member.delete()
            member.purge()

    def test_canAccess(self):
        self.failUnless(self.view.canAccess())


class TestMemberDeleteView(MemberViewTestCase):
    "Visitor can't remove Levin from Administration project."

    viewClass = MemberDeleteView


class TestMemberDeleteViewLevin(MemberViewTestCase):
    "Levin can remove Levin from Administration project."

    viewClass = MemberDeleteView
    viewerName = 'levin'
    personName = 'levin'
    requiredResponseClassName = 'HttpResponse'
    requiredRedirect = ''

    def setUp(self):
        super(TestMemberDeleteViewLevin, self).setUp()
        person = self.registry.persons[self.personName]
        role = self.registry.roles['Friend']
        self.registry.projects[self.projectName].members.create(person, role=role)
    
    def tearDown(self):
        super(TestMemberDeleteViewLevin, self).tearDown()
        person = self.registry.persons[self.personName]
        if person in self.registry.projects[self.projectName].members:
            member = self.registry.projects[self.projectName].members[person]
            member.delete()
            member.purge()

    def test_canAccess(self):
        self.failUnless(self.view.canAccess())


class TestMemberDeleteViewLevinPOST(MemberViewTestCase):
    "Levin can remove Levin from Administration project."

    viewClass = MemberDeleteView
    viewerName = 'levin'
    personName = 'levin'
    POST = MultiValueDict({'Submit': ['Delete membership']})
    requiredRedirect = '/person/home/'

    def setUp(self):
        super(TestMemberDeleteViewLevinPOST, self).setUp()
        person = self.registry.persons[self.personName]
        role = self.registry.roles['Friend']
        self.registry.projects[self.projectName].members.create(person, role=role)
    
    def tearDown(self):
        super(TestMemberDeleteViewLevinPOST, self).tearDown()
        person = self.registry.persons[self.personName]
        if person in self.registry.projects[self.projectName].members:
            member = self.registry.projects[self.projectName].members[person]
            member.delete()
            member.purge()

    def test_canAccess(self):
        self.failUnless(self.view.canAccess())


class TestMemberDeleteViewAdministrator(TestMemberDeleteViewLevin):
    "Administrator can remove Levin from Administration project."

    viewerName = 'admin'


class TestMemberDeleteViewAdministratorPOST(TestMemberDeleteViewLevinPOST):
    "Administrator can remove Levin from Administration project."

    viewerName = 'admin'
    requiredRedirect = '/project/administration/members/'


class TestMemberDeleteViewNatasha(MemberViewTestCase):
    "Natasha can't remove Levin from Administration project."

    viewClass = MemberDeleteView
    viewerName = 'natasha'
    personName = 'levin'
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/accessDenied/'

    def setUp(self):
        super(TestMemberDeleteViewNatasha, self).setUp()
        person = self.registry.persons[self.personName]
        role = self.registry.roles['Friend']
        self.registry.projects[self.projectName].members.create(person, role=role)
    
    def tearDown(self):
        super(TestMemberDeleteViewNatasha, self).tearDown()
        person = self.registry.persons[self.personName]
        if person in self.registry.projects[self.projectName].members:
            member = self.registry.projects[self.projectName].members[person]
            member.delete()
            member.purge()

    def test_canAccess(self):
        self.failIf(self.view.canAccess())


class TestMemberDeleteViewNatashaPOST(MemberViewTestCase):
    "Natasha can't remove Levin from Administration project."

    viewClass = MemberDeleteView
    viewerName = 'natasha'
    personName = 'levin'
    POST = MultiValueDict({'Submit': ['Delete membership']})
    requiredResponseClassName = 'HttpResponseRedirect'
    requiredRedirect = '/accessDenied/'

    def setUp(self):
        super(TestMemberDeleteViewNatashaPOST, self).setUp()
        person = self.registry.persons[self.personName]
        role = self.registry.roles['Friend']
        self.registry.projects[self.projectName].members.create(person, role=role)
    
    def tearDown(self):
        super(TestMemberDeleteViewNatashaPOST, self).tearDown()
        person = self.registry.persons[self.personName]
        if person in self.registry.projects[self.projectName].members:
            member = self.registry.projects[self.projectName].members[person]
            member.delete()
            member.purge()

    def test_canAccess(self):
        self.failIf(self.view.canAccess())

