from provide.plugin.base import VirtualenvDomainModelApplicationPlugin

class Plugin(VirtualenvDomainModelApplicationPlugin):

    installerScriptUrl = 'http://appropriatesoftware.net/provide/docs/scanbooker-virtualenv'
    installerScriptPath = './scanbooker-virtualenv'
    applicationTitle = 'ScanBooker'
    makeconfigScriptPath = './scanbooker-makeconfig'
    adminScriptPath = './scanbooker-admin'
    testScriptPath = './scanbooker-test'
    configEnvvarName = 'SCANBOOKER_SETTINGS'

