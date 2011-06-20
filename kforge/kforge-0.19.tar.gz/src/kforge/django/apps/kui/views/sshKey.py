from kforge.django.apps.kui.views.personHasMany import PersonHasManyView
from dm.view.base import AbstractListHasManyView
from dm.view.base import AbstractCreateHasManyView
from dm.view.base import AbstractReadHasManyView
from dm.view.base import AbstractUpdateHasManyView
from dm.view.base import AbstractDeleteHasManyView
from kforge.django.apps.kui.views import manipulator
import kforge.command

class SshKeyView(PersonHasManyView):

    hasManyKeyName = 'SshKey'

    def __init__(self, **kwds):
        super(SshKeyView, self).__init__(hasManyName='sshKeys', **kwds)
        if not self.isSshPluginEnabled():
            self.setRedirect('/person/home/')

    def getManipulatorClass(self):
        return manipulator.SshKeyCreateManipulator
        
    def setContext(self):
        super(SshKeyView, self).setContext()
        self.context.update({
            'sshKey'         : self.getAssociationObject(),
        })

    def setMajorNavigationItem(self):
        self.majorNavigationItem = '/person/home/'

    def setMinorNavigationItem(self):
        self.minorNavigationItem = '/person/%s/sshKeys/create/' % self.domainObjectKey

    def canCreateSshKey(self):
        return self.canUpdatePerson()
    
    def canReadSshKey(self):
        return self.canUpdatePerson()

    def canDeleteSshKey(self):
        return self.canUpdatePerson()


class SshKeyCreateView(SshKeyView, AbstractCreateHasManyView):

    templatePath = 'sshKey/create'

    def canAccess(self):
        return self.canCreateSshKey()
        
    def makePostManipulateLocation(self):
        return '/person/%s/' % (
            self.domainObjectKey
        )


class SshKeyDeleteView(SshKeyView, AbstractDeleteHasManyView):

    templatePath = 'sshKey/delete'
    
    def canAccess(self):
        return self.canDeleteSshKey()

    def makePostManipulateLocation(self):
        return '/person/%s/' % (
            self.domainObjectKey
        )



def create(request, personName, returnPath=''):   
    view = SshKeyCreateView(request=request, domainObjectKey=personName)
    return view.getResponse()

def delete(request, personName, sshKeyId):
    view = SshKeyDeleteView(request=request, domainObjectKey=personName, hasManyKey=sshKeyId)
    return view.getResponse()

