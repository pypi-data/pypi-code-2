from dm.view.base import *
from kforge.django.apps.kui.views.base import KforgeView
from kforge.django.apps.kui.views import manipulator
from kforge.exceptions import KforgeCommandError
import kforge.command
import kforge.accesscontrol
from kforge.command.emailjoinrequest import EmailJoinRequest

class AbstractProjectView(AbstractClassView, KforgeView):

    domainClassName = 'Project'
    majorNavigationItem = '/project/'


class ProjectClassView(AbstractProjectView):

    minorNavigation = [
        {'title': 'Index', 'url': '/project/'},
        {'title': 'Search', 'url': '/project/search/'},
        {'title': 'Register', 'url': '/project/create/'},
    ]
    minorNavigationItem = '/project/'
    
    def __init__(self, **kwds):
        super(ProjectClassView, self).__init__(**kwds)
        self.project = None

    def setContext(self):
        super(ProjectClassView, self).setContext()
        self.context.update({
            'project'         : self.getDomainObject(),
        })

    def getDomainObject(self):
        super(ProjectClassView, self).getDomainObject()
        self.project = self.domainObject
        return self.project

    def getProject(self):
        return self.getDomainObject()

    def isAuthorised(self, **kwds):
        kwds['project'] = self.getProject()
        return self.accessController.isAuthorised(**kwds)


class ProjectListView(ProjectClassView, AbstractListView):

    templatePath = 'project/list'
    minorNavigationItem = '/project/'

    def canAccess(self):
        return self.canReadProject()


class ProjectSearchView(ProjectClassView, AbstractSearchView):

    templatePath = 'project/search'
    minorNavigationItem = '/project/search/'
    
    def canAccess(self):
        return self.canReadProject()


class ProjectCreateView(ProjectClassView, AbstractCreateView):

    templatePath = 'project/create'
    minorNavigationItem = '/project/create/'

    def getManipulatorClass(self):
        return manipulator.ProjectCreateManipulator
        
    def canAccess(self):
        return self.canCreateProject()
        
    def makePostManipulateLocation(self):
        return '/project/%s/' % self.getDomainObject().getRegisterKeyValue()

    def manipulateDomainObject(self):
        super(ProjectCreateView, self).manipulateDomainObject()
        if not self.getFormErrors():
            if not self.domainObject:
                raise "View did not produce an object."
            memberCommandClass = self.commands['MemberCreate']
            project = self.domainObject
            person = self.session.person
            roleName = 'Administrator'
            role = self.registry.roles[roleName]
            memberCommand = memberCommandClass(
                project=project, person=person, role=role
            )
            memberCommand.execute()


class ProjectInstanceView(ProjectClassView):

    def setMinorNavigationItems(self):
        project = self.getDomainObject()
        projectMenuTitle = project.title or project.name
        self.minorNavigation = [
            {
                'title': projectMenuTitle.capitalize(),
                'url': '/project/%s/' % self.domainObjectKey
            },
            {
                'title': 'Members',
                'url': '/project/%s/members/' % self.domainObjectKey
            },
            {
                'title': 'Services',
                'url': '/project/%s/services/' % self.domainObjectKey
            },
        ]

    def setMinorNavigationItem(self):
        self.minorNavigationItem = '/project/%s/' % self.domainObjectKey


class ProjectReadView(ProjectInstanceView, AbstractReadView):

    templatePath = 'project/read'
    minorNavigationItem = '/project/'

    def canAccess(self):
        if not self.getDomainObject():
            return False
        return self.canReadProject()

    def canJoinProject(self):
        if self.session is None or self.session.person is None \
            or self.session.person in self.project.members or self.session.person in self.project.pending_members:
            return False
        return True


class ProjectUpdateView(ProjectInstanceView, AbstractUpdateView):

    templatePath = 'project/update'

    def getManipulatorClass(self):
        return manipulator.ProjectUpdateManipulator

    def canAccess(self):
        if not self.getDomainObject():
            msg = "Access Denied: No domain object on project update view."
            self.logger.debug(msg)
            return False
        return self.canUpdateProject()

    def makePostManipulateLocation(self):
        return '/project/%s/' % self.getDomainObject().getRegisterKeyValue()


class ProjectDeleteView(ProjectInstanceView, AbstractDeleteView):

    templatePath = 'project/delete'

    def canAccess(self):
        if not self.getDomainObject():
            return False
        return self.canDeleteProject()

    def makePostManipulateLocation(self):
        return '/project/'


class ProjectJoinView(ProjectInstanceView, AbstractReadView):

    templatePath = 'project/join'

    def canAccess(self):
        if not self.getDomainObject() or self.session is None or self.session.person is None:
            msg = "Non logged in person attempting to join a project"
            self.logger.debug(msg)
            return False
        #We'll just add the member to the list when they view the page rather than
        #making them click a button
        person = self.session.person
        project = self.getDomainObject()
        self.logger.debug(person)
        self.logger.debug(project)
        memberCommand = kforge.command.PendingMemberCreate(
            project=project, person=person
        )
        memberCommand.execute()

        #We'll also send an e-mail to the project administrators about it
        emailCommand = EmailJoinRequest(project, person)
        emailCommand.execute()

        return True

def list(request):
    view = ProjectListView(request=request)
    return view.getResponse()

def search(request, startsWith=''):
    view = ProjectSearchView(request=request, startsWith=startsWith)
    return view.getResponse()

def create(request, returnPath=''):
    view = ProjectCreateView(request=request)
    return view.getResponse()

def read(request, projectName=''):
    view = ProjectReadView(request=request, domainObjectKey=projectName)
    return view.getResponse()

def update(request, projectName):
    view = ProjectUpdateView(request=request, domainObjectKey=projectName)
    return view.getResponse()

def delete(request, projectName):
    view = ProjectDeleteView(request=request, domainObjectKey=projectName)
    return view.getResponse()

def join(request, projectName):
    view = ProjectJoinView(request=request, domainObjectKey=projectName)
    return view.getResponse()

