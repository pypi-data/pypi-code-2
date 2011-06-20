from dm.dom.stateful import *

class Member(DatedStatefulObject):
    """
    Registers membership of a project by a person. 
    Associates a Person, a Project, and a Role.
    """

    project = HasA('Project')
    person  = HasA('Person')
    role    = HasA('Role', default=StatefulObject.dictionary['member_role'])

    isUnique = False

    def initialise(self, register=None):
        super(Member, self).initialise(register)
        if not self.role:
            roleName = self.dictionary['member_role']
            self.role = self.registry.roles[roleName]
            self.isChanged = True

    def purge (self):
        super(Member, self).purge()
        self.project = None
        self.person = None
        self.role = None

    def getLabelValue(self):
        return "%s-%s" % (
            self.person.getLabelValue(),
            self.project.getLabelValue(),
        )   

class PendingMember(DatedStatefulObject):
    """
    Registers membership of a project by a person. 
    Associates a Person, a Project, and a Role.
    """

    project = HasA('Project')
    person  = HasA('Person')

    isUnique = False

    def initialise(self, register=None):
        super(PendingMember, self).initialise(register)

    def purge (self):
        super(PendingMember, self).purge()
        self.project = None
        self.person = None

    def getLabelValue(self):
        return "%s-%s" % (
            self.person.getLabelValue(),
            self.project.getLabelValue(),
        )   
