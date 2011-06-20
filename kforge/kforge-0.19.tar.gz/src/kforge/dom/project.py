from dm.dom.stateful import *

def getPlugins():
    return DomainRegistry().plugins

class Project(StandardObject):
    "Registered project."

    searchAttributeNames = ['name', 'title', 'description']

    title       = String(default='')
    description = String(default='')
    licenses    = AggregatesMany('ProjectLicense', 'license')
    members     = AggregatesMany('Member', 'person')
    pending_members = AggregatesMany('PendingMember', 'person')
    services    = AggregatesMany('Service', 'name')

    isUnique = False

    def getLabelValue(self):
        return self.title or self.name

