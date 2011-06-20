from dm.accesscontrol import SystemAccessController
from kforge.exceptions import *

class ProjectAccessController(SystemAccessController):
    "Introduces project role possibilities to access controller."

    def isAccessAuthorised(self, project=None, **kwds):
        self.project = project
        return super(ProjectAccessController, self).isAccessAuthorised(**kwds)

    def assertAccessNotAuthorised(self):
        self.assertMembershipNotAuthorised()
        super(ProjectAccessController, self).assertAccessNotAuthorised()

    def assertMembershipNotAuthorised(self):
        if self.project:
            try:
                role = self.person.memberships[self.project].role
            except KforgeRegistryKeyError, inst:
                pass
            else:
                self.assertRoleNotAuthorised(role, "project %s role" % role.name.lower())
            if not self.alsoCheckVisitor():
                return
            try:
                role = self.getVisitor().memberships[self.project].role
            except KforgeRegistryKeyError, inst:
                pass
            else: 
                self.assertRoleNotAuthorised(role, "visitor's project %s role" % role.name.lower())

    def makeMemoName(self, person, actionName, protectedObject):
        # Make sure service plugin memo names are distinct between projects.
        # Todo: Change service access control to use service object.
        memoName = super(ProjectAccessController, self).makeMemoName(person, actionName, protectedObject)
        if self.project:
            projectTag = self.project.id
        else:
            projectTag = None
        memoName = "Project.%s.%s" % (projectTag, memoName)
        return memoName

