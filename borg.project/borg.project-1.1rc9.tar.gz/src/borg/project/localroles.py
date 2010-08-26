from zope.interface import implements
from zope.component import adapts

from borg.localrole.interfaces import ILocalRoleProvider
from borg.project.interfaces import IProject

class LocalRoles(object):
    """Provide a local role manager for projects
    """
    implements(ILocalRoleProvider)
    adapts(IProject)

    def __init__(self, context):
        self.context = context

    def getAllRoles(self):
        for m in self.context.managers:
            yield (m, ('Manager',))
        for m in self.context.members:
            yield (m, ('TeamMember',))
        for m in self.context.groups:
            yield (m, ('TeamMember',))

    def getRoles(self, principal_id):
        roles = set()
        if principal_id in self.context.managers:
            roles.add('Manager')
        if principal_id in self.context.members:
            roles.add('TeamMember')
        if principal_id in self.context.groups:
            roles.add('TeamMember')
        return roles
