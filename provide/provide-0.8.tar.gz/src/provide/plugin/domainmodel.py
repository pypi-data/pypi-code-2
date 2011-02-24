from provide.plugin.base import VirtualenvDomainModelApplicationPlugin
import os

class Plugin(VirtualenvDomainModelApplicationPlugin):

    makeconfigScriptPath = './domainmodel-makeconfig'
    testScriptPath = './domainmodel-test'
    adminScriptPath = './domainmodel-admin'
    configEnvvarName = 'DOMAINMODEL_SETTINGS'

    def readExampleConfigFile(self, service):
        f = self.getStream(service, 'data/etc/domainmodel.conf.new')
        configContent = f.read()
        f.close()
        return configContent

    def getStream(self, service, filePath):
        libPath = self.fs.makeLibPythonPath(service)
        resPath = os.path.join(libPath, 'dm', filePath)
        return open(resPath, 'r')

    def setTemplates(self, service):
        self.setTemplate(service, 'index.html')

    def setTemplate(self, service, templateName):
        f = self.getStream(service, os.path.join('django', 'templates', templateName))
        content = f.read()
        f.close()
        templatesPath = self.fs.makeTemplatesPath(service)
        if not os.path.exists(templatesPath):
            os.makedirs(templatesPath)
        filePath = os.path.join(templatesPath, templateName)
        f = open(filePath, 'w')
        f.write(content)
        f.close()
        os.chmod(filePath, 0444)
    
    def buildApacheConfig(self, service):
        pass
