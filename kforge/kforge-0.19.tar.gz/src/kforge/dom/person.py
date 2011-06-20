from dm.dom.stateful import *
import dm.dom.person

class Person(dm.dom.person.Person):
    "Registered person."

    memberships = AggregatesMany('Member', 'project')
    pending_memberships = AggregatesMany('PendingMember', 'project')
    sshKeys = AggregatesMany('SshKey', 'id')

    isUnique = False

    def getLabelValue(self):
        return self.fullname or self.name

    def getFirstName(self):
        name = self.getLabelValue()
        parts = name.strip().split(' ')
        return parts[0]

# Todo: Remove, since they repeat the work of 'AggregatesMany'?
#    def delete(self):
#        for member in self.memberships:
#            member.delete()
#        super(Person, self).delete()
#
#    def purge(self):
#        for member in self.memberships.getAll():
#            member.delete()
#            member.purge()
#        super(Person, self).purge()


class SshKey(DatedStatefulObject):

    searchAttributeNames = ['keyString']

    keyString = Text()
    person = HasA('Person')
    isConsummated = Boolean()

