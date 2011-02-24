from provide.plugin.base import VirtualenvDomainModelApplicationPlugin
import os

class Plugin(VirtualenvDomainModelApplicationPlugin):

    installerScriptUrl = 'http://appropriatesoftware.net/provide/docs/quant-virtualenv'
    installerScriptPath = './quant-virtualenv'
    makeconfigScriptPath = './quant-makeconfig'
    adminScriptPath = './quant-admin'
    testScriptPath = './quant-test'
    configEnvvarName = 'QUANT_SETTINGS'


