from dm.dom.stateful import *

class License(SimpleNamedObject):
    "Registered Open Knowledge license."

    isConstant = True
    registerKeyName = 'id'

    def getLabelValue(self):
        return self.name

class ProjectLicense(SimpleObject):
    "Registered usage of a License by a Project."

    project = HasA('Project')
    license = HasA('License')

    def getLabelValue(self):
        return "%s-%s" % (
            self.project.getLabelValue(),
            self.license.getLabelValue(),
        )
    
