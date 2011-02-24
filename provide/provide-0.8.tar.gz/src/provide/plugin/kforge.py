from provide.plugin.base import VirtualenvDomainModelApplicationPlugin
import os

class Plugin(VirtualenvDomainModelApplicationPlugin):

    installerScriptUrl = 'http://appropriatesoftware.net/provide/docs/kforge-virtualenv'
    installerScriptPath = './kforge-virtualenv'
    makeconfigScriptPath = './kforge-makeconfig'
    adminScriptPath = './kforge-admin'
    testScriptPath = './kforge-test'
    configEnvvarName = 'KFORGE_SETTINGS'

    def makeConfigArguments(self, service):
        arguments = super(Plugin, self).makeConfigArguments(service)
        #if options.projectDataDir != None:
        #    arguments.append("--%s=%s" % ('project-data-dir', options.projectDataDir))
        veBinPath = self.fs.makeVeBinPath(service.application)
        tracAdminPath = self.join(veBinPath, 'trac-admin')
        if os.path.exists(tracAdminPath):
            arguments.append("--trac-admin=%s" % tracAdminPath)
        arguments.append("--kforge-apache-config=%s" % self.fs.makeServiceApacheConfigPath(service))
        return arguments

