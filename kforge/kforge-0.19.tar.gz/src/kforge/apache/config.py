from dm.apache.config import ApacheConfigBuilder
from kforge.exceptions import MissingPluginSystem
from kforge.ioc import *
import dm.environment
import kforge.accesscontrol
import dm.environment
import kforge.url
import commands
from kforge.dictionarywords import *

class ApacheConfigBuilder(ApacheConfigBuilder):
    
    registry = RequiredFeature('DomainRegistry')
    fsPathBuilder = RequiredFeature('FileSystem')
    
    def __init__(self):
        super(ApacheConfigBuilder, self).__init__()
        self.url_scheme = kforge.url.UrlScheme()
    
    def createConfigContent(self):
        webuiConfig = super(ApacheConfigBuilder, self).createConfigContent()
        servicesConfig = self.createServicesConfig()
        if self.dictionary[APACHE_PYTHON_MODULE] == 'mod_wsgi':
            config = servicesConfig + webuiConfig
        elif self.dictionary[APACHE_PYTHON_MODULE] == 'mod_python':
            config = webuiConfig + servicesConfig
        return config

    def buildWsgiFile(self):
        super(ApacheConfigBuilder, self).buildWsgiFile()
        for plugin in self.registry.plugins:
            plugin.buildWsgiFile()
   
    def buildCgiFile(self):
        super(ApacheConfigBuilder, self).buildCgiFile()
        for plugin in self.registry.plugins:
            plugin.buildCgiFile()
   
    def getWsgiHandlerModule(self):
        return 'kforge.handlers.kui.wsgi'

    def getModPythonHandlerModuleVirtualenv(self):
        systemName = self.dictionary[SYSTEM_NAME]
        moduleName = '%s.handlers.kui.modpython' % systemName
        return moduleName

    def getWebuiPathPatterns(self):
        paths = '^%s$' % self.url_scheme.url_for('home')
        extraPaths = [
            self.url_scheme.url_for('feed'),
            self.url_scheme.url_for('access_denied'),
            self.url_scheme.url_for('login'),
            self.url_scheme.url_for('logout'),
            self.url_scheme.url_for('admin'),
            self.url_scheme.url_for('person'),
            self.url_scheme.url_for('project'),
        ]
        for path in extraPaths:
            paths += '|^%s($|/.*)' % path
        return paths

    def createServicesConfig(self):
        urlBuilder = kforge.url.UrlScheme()
        config = '''
# Project services.
'''
        config += self.getEnvironmentVariables()
        config += self.getPluginsCommonConfig()
        for project in self.registry.projects:
            serviceNames = project.services.keys()
            # Need names in reverse sorted order (so shorter names don't longer ones).
            serviceNames.sort()
            serviceNames.reverse()
            for name in serviceNames:
                config += self.getServiceSection(urlBuilder, project.services[name])
        return config
        
    def getEnvironmentVariables(self):
        configVars = self.getConfigVars()
        if self.dictionary[APACHE_PYTHON_MODULE] == 'mod_wsgi':
            config = "\n" 
        else:
            systemConfigEnvVarName = self.environment.getConfigFilePathEnvironmentVariableName()
            systemConfigFilePath = self.environment.getConfigFilePath()
            config = """
SetEnv DJANGO_SETTINGS_MODULE kforge.django.settings.main
SetEnv %(CONFIG_ENV_VAR_NAME)s %(SYSTEM_CONFIG_PATH)s
SetEnv PYTHONPATH %(PYTHON_PATH)s
            """ % configVars
        return config
    
    def getPluginsCommonConfig(self):
        configSnippet = ''
        for plugin in self.registry.plugins:
            configSnippet += plugin.getApacheConfigCommon()
        return '\n' + configSnippet
    
    def getServiceSection(self, urlBuilder, service):
        "Generates Apache config fragment for service."
        if not service.plugin:
            msg = "No apache config without plugin on service: %s" % service
            self.logger.warning(msg)
            return "\n# %s\n" % msg
        pluginSystem = service.plugin.getSystem()
        apacheConfigTemplate = pluginSystem.getApacheConfig(service)
        uriPrefix = self.dictionary[URI_PREFIX]
        serviceUrl = urlBuilder.getServicePath(service)
        serviceUrlNoPrefix = serviceUrl.replace(uriPrefix, '', 1)
        varDict = {}
        varDict['uriPrefix'] = uriPrefix
        varDict['urlPath'] = serviceUrl
        varDict['urlPathNoPrefix'] = serviceUrlNoPrefix
        varDict['fileSystemPath'] = self.fsPathBuilder.getServicePath(service)
        varDict['accessControl'] = self.getAccessControl()
        varDict['modPythonAccessControl'] = self.getModPythonAccessControl()
        return '\n' + apacheConfigTemplate % varDict
    
    def getAccessControl(self):
        """
        Get access control fragment.
        """
        configVars = self.getConfigVars()
        if self.dictionary[APACHE_PYTHON_MODULE] == 'mod_wsgi':
            config = self.getModWsgiAccessControl()
        elif self.dictionary[APACHE_PYTHON_MODULE] == 'mod_python':
            config = self.getModPythonAccessControl()
        return config

    def getModWsgiAccessControl(self):
        config = """AuthType basic
AuthName "%(HTTP_AUTH_REALM)s Restricted Area"
AuthBasicProvider wsgi
WSGIAuthUserScript %(WSGI_SCRIPT_PATH)s
Require valid-user""" % self.getConfigVars()
        return config

    def getModPythonAccessControl(self):
        if self.dictionary[VIRTUALENVBIN_PATH]:
            accessHandlerName = 'kforgevirtualenvhandlers::accesshandler'
            authenHandlerName = 'kforgevirtualenvhandlers::authenhandler'
        else:
            accessHandlerName = 'kforge.handlers.projecthost::accesshandler'
            authenHandlerName = 'kforge.handlers.projecthost::authenhandler'
        modPythonAccessControl = """
# Need to set DJANGO as used in both project (auth) and admin
# Set as PYTHONOPTION as SetEnv does not seem to work in here
PYTHONOPTION DJANGO_SETTINGS_MODULE kforge.django.settings.main
PYTHONOPTION %s %s
PythonPath "'%s'.split(':') + sys.path"
PythonDebug %s

# For details see comments in kforge.handlers.projecthost.py
Satisfy any
PythonAccessHandler %s
PythonAuthenHandler %s
AuthType basic
AuthName "%s Restricted Area"
Require valid-user
# Only available in mod_auth_basic available in apache >= 2.1
<IfModule mod_auth_basic.c>
    AuthBasicAuthoritative Off
    AuthUserFile /dev/null
</IfModule>
""" % (
                self.systemConfigEnvVarName,
                self.dictionary[SYSTEM_CONFIG_PATH],
                self.dictionary[PYTHONPATH],
                self.getPythonDebugMode(),
                accessHandlerName,
                authenHandlerName,
                self.dictionary[HTTP_AUTH_REALM].decode('utf-8'),
        )
        return modPythonAccessControl

    def createWsgiScriptContent(self):
        content = super(ApacheConfigBuilder, self).createWsgiScriptContent()
        content += """
def check_password(environ, user, password):
    from kforge.handlers.modwsgi import WsgiCheckPasswordHandler
    application = WsgiCheckPasswordHandler()
    return application(environ, user, password)
""" 
        return content

