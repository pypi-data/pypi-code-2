from dm.dom.stateful import *
import os

class Service(StandardObject):
    "Project service."

    registerKeyName = 'id'

    plugin  = HasA('Plugin')
    project = HasA('Project')

    projectUrls = RequiredFeature('UrlScheme')

    isUnique = False

    def checkProjectPluginDir(self):
        if not self.hasProjectPluginDir():
            self.createProjectPluginDir()

    def hasProjectPluginDir(self):
        return os.path.exists(self.getProjectPluginDirPath())

    def createProjectPluginDir(self):
        if not self.hasProjectPluginDir():
            os.makedirs(self.getProjectPluginDirPath())

    def getProjectPluginDirPath(self):
        return self.paths.getProjectPluginPath(self.project, self.plugin)

    def hasDir(self):
        return os.path.exists(self.getDirPath())

    def createDir(self):
        if not self.hasDir():
            os.makedirs(self.getDirPath())

    def getDirPath(self):
        return self.paths.getServicePath(self)

    def getUrlPath(self):
        return self.projectUrls.getServicePath(self)

    def getUrl(self):
        return self.projectUrls.getServiceUrl(self)

    def getUserHelp(self, serviceLocation):
        return self.plugin.getSystem().getUserHelp(self, serviceLocation)

    def getStatusMessage(self):
        return self.plugin.getSystem().getStatusMessage(self)

    def getLabelValue(self):
        return "%s-%s" % (
            self.project.getLabelValue(),
            self.name,
        )

    def getExtnRegister(self):
        return self.plugin.getExtnRegister()

    def getExtnObject(self):
        return self.plugin.getExtnObject(self)

