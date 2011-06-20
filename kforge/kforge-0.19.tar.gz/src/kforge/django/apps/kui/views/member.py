from kforge.django.apps.kui.views.projectHasMany import ProjectHasManyView
from dm.view.base import AbstractListHasManyView
from dm.view.base import AbstractCreateHasManyView
from dm.view.base import AbstractReadHasManyView
from dm.view.base import AbstractUpdateHasManyView
from dm.view.base import AbstractDeleteHasManyView
from kforge.django.apps.kui.views import manipulator
import kforge.command

from kforge.command.emailjoinrequest import EmailJoinApprove, EmailJoinReject

class MemberView(ProjectHasManyView):

    hasManyClassName = 'Member'

    def __init__(self, list_name='members', **kwds):
        super(MemberView, self).__init__(hasManyName=list_name, **kwds)

    def setContext(self):
        super(MemberView, self).setContext()
        self.context.update({
            'member' : self.getAssociationObject(),
        })

    def setMinorNavigationItem(self):
        self.minorNavigationItem = '/project/%s/members/' % self.domainObjectKey


class MemberListView(MemberView, AbstractListHasManyView):

    templatePath = 'member/list'
    
    def canAccess(self):
        return self.canReadProject()


class MemberCreateView(MemberView, AbstractCreateHasManyView):

    templatePath = 'member/create'
    
    def canAccess(self):
        return self.canCreateMember()

    def makePostManipulateLocation(self):
        return '/project/%s/%s/' % (
            self.domainObjectKey, self.hasManyName
        )

    def getManipulatorClass(self):
        return manipulator.MemberCreateManipulator

    def manipulateDomainObject(self):
        #We want to make sure that if this member is pending, we remove them from that list
        super(MemberCreateView, self).manipulateDomainObject()
        if not self.getFormErrors():
            if not self.domainObject:
                raise "View did not produce an object."
            project = self.domainObject
            form = self.getForm()
            personName = form['person'].data
            person = self.registry.persons[personName]
            if person in project.pending_members:
                memberCommand = kforge.command.PendingMemberDelete(
                    projectName=project.name, personName=person.name
                )
                memberCommand.execute()
                msg = "Deleted member %s from pending list for project %s since they were added as a member" % (person.name, project.name)
                self.logger.debug(msg)


class MemberUpdateView(MemberView, AbstractUpdateHasManyView):

    templatePath = 'member/update'
    
    def canAccess(self):
        return self.canUpdateMember()

    def makePostManipulateLocation(self):
        return '/project/%s/%s/' % (
            self.domainObjectKey, self.hasManyName
        )

    def getManipulatorClass(self):
        return manipulator.MemberUpdateManipulator


class MemberDeleteView(MemberView, AbstractDeleteHasManyView):

    templatePath = 'member/delete'
    
    def canAccess(self):
        self.member = self.getAssociationObject()
        return self.canDeleteMember()

    def makePostManipulateLocation(self):
        if self.session.person == self.member.person:
            return '/person/home/'
        else:
            return '/project/%s/%s/' % (
                self.domainObjectKey, self.hasManyName
            )


class MemberRejectView(MemberView, AbstractDeleteHasManyView):

    templatePath = 'member/reject'
    
    def canAccess(self):
        return self.canCreateMember()

    def makePostManipulateLocation(self):
        return '/project/%s/members/' % (
            self.domainObjectKey
        )

    def manipulateDomainObject(self):
        super(MemberRejectView, self).manipulateDomainObject()
        #we'll also send an e-mail to the member letting them know they got rejected
        project = self.domainObject
        person = self.registry.persons[self.hasManyKey]
        emailCommand = EmailJoinReject(project, person)
        emailCommand.execute()

class MemberApproveView(MemberView, AbstractDeleteHasManyView):

    templatePath = 'member/approve'
    
    def canAccess(self):
        return self.canCreateMember()

    def makePostManipulateLocation(self):
        return '/project/%s/members/' % (
            self.domainObjectKey
        )

    def getManipulatorClass(self):
        return manipulator.MemberUpdateManipulator

    def manipulateDomainObject(self):
        super(MemberApproveView, self).manipulateDomainObject()
        if not self.getFormErrors():
            if not self.domainObject:
                raise "View did not produce an object."
            form = self.getForm()
            roleName = form['role'].data
            role = self.registry.roles[roleName]
            project = self.domainObject
            person = self.registry.persons[self.hasManyKey]
            memberCommand = kforge.command.MemberCreate(
                project=project, person=person, role=role
            )
            memberCommand.execute()
            msg = "Approved member %s for project %s" % (person.name, project.name)
            self.logger.debug(msg)

            #we'll also send an e-mail to the member letting them know they got approved
            emailCommand = EmailJoinApprove(project, person)
            emailCommand.execute()


def list(request, projectName=''):
    view = MemberListView(
        request=request,
        domainObjectKey=projectName,
    )
    return view.getResponse()
    
def create(request, projectName=''):
    view = MemberCreateView(
        request=request,
        domainObjectKey=projectName,
    )
    return view.getResponse()
    
def update(request, projectName='', personName=''):
    view = MemberUpdateView(
        request=request,
        domainObjectKey=projectName,
        hasManyKey=personName,
    )
    return view.getResponse()
    
def delete(request, projectName='', personName=''):
    view = MemberDeleteView(
        request=request,
        domainObjectKey=projectName,
        hasManyKey=personName,
    )
    return view.getResponse()

def approve(request, projectName='', personName=''):
    view = MemberApproveView(
        list_name='pending_members',
        request=request,
        domainObjectKey=projectName,
        hasManyKey=personName,
    )
    return view.getResponse()

def reject(request, projectName='', personName=''):
    view = MemberRejectView(
        list_name='pending_members',
        request=request,
        domainObjectKey=projectName,
        hasManyKey=personName,
    )
    return view.getResponse()

