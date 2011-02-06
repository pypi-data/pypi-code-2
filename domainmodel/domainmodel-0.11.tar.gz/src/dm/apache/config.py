from dm.ioc import RequiredFeature
from dm.dictionarywords import *
from dm.environment import SystemEnvironment
import commands
import os

class ApacheConfigBuilder(object):

    dictionary = RequiredFeature('SystemDictionary')
    logger = RequiredFeature('Logger')
    debug = RequiredFeature('Debug')

    def __init__(self):
        self.initEnvironment()
        self.initPythonDebugMode()
        self.initConfigEnvVarName()
        self.initConfigFilePath()

    def initEnvironment(self):
        systemName = self.dictionary[SYSTEM_NAME]
        self.environment = SystemEnvironment(systemName)

    def initPythonDebugMode(self):
        if self.dictionary[SYSTEM_MODE] == 'production':
            self.pythonDebugMode = 'Off'
        else:
            self.pythonDebugMode = 'On'

    def initConfigEnvVarName(self):
        varName = self.environment.getConfigFilePathEnvironmentVariableName()
        self.systemConfigEnvVarName = varName

    def initConfigFilePath(self):
        self.systemConfigFilePath = self.environment.getConfigFilePath()

    def reloadConfig(self):
        """
        Reloads config into Apache.
        """
        # todo: Check the return value of reloadConfig() is necessary.
        if self.dictionary[SKIP_APACHE_RELOAD]:
            msg = "%s: Not reloading Apache since '%s' is set." % (self.__class__.__name__, SKIP_APACHE_RELOAD)
            self.logger.warning(msg)
            print "Warning:", msg
        elif not self.dictionary[APACHE_RELOAD_CMD]:
            msg = "%s: Not reloading apache since '%s' command is not set." % (self.__class__.__name__, APACHE_RELOAD_CMD)
            self.logger.error(msg)
        else:
            cmd = self.dictionary[APACHE_RELOAD_CMD]
            msg = "%s: Reloading apache with command: %s" % (self.__class__.__name__, cmd)
            self.logger.info(msg)
            try:
                status, output = commands.getstatusoutput(cmd)
                if status:
                    msg = "%s:" % self.__class__.__name__
                    msg += " Apache reload command '%s' exited with" % cmd
                    msg += " non-zero status %s: %s" % (status, output)
                    self.logger.error(msg)
                    return False
            except Exception, inst:
                self.logger.error('Exception on reload of apache: %s' % inst)
                return False
        return True

    def getConfigPath(self):
        return self.dictionary[APACHE_CONFIG_PATH]

    def buildConfigFile(self):
        """
        Creates config content, and writes to config file.
        """
        configPath = self.getConfigPath()
        if not configPath:
            msg = "No Apache configuration file path has been provided. Try setting '%s' in the configuration file: %s" % (APACHE_CONFIG_PATH, self.dictionary.configFilePath)
            raise Exception(msg)
        configContent = self.createConfigContent()
        self.writeFile(configPath, configContent, 'Apache config')

    def writeFile(self, path, content, purpose):
        path = os.path.normpath(path)
        parent = os.path.dirname(path)
        if not os.path.exists(parent):
            os.makedirs(parent)
        content = content.encode('utf-8', 'ignore')
        # Todo: Make this filewriting safer.
        file = open(path, 'w')
        file.write(content)
        file.close()
        self.logger.info("%s: Written new %s to path: %s" % (purpose, self.__class__.__name__, path))

    def createConfigContent(self):
        # Assemble variables.
        configVars = {}
        configVars['CONFIG_ENV_VAR_NAME'] = self.environment.getConfigFilePathEnvironmentVariableName()
        configVars['SYSTEM_TITLE'] = self.dictionary[SYSTEM_TITLE]
        configVars['SYSTEM_CONFIG_PATH'] = self.dictionary[SYSTEM_CONFIG_PATH]
        configVars['WSGI_SCRIPT_PATH'] = self.dictionary[WSGI_SCRIPT_PATH]
        configVars['WSGI_SCRIPT_ALIAS'] = self.noSlash(self.dictionary[URI_PREFIX]) or '/'
        configVars['PYTHON_PATH'] = self.noSlash(self.dictionary[PYTHONPATH])
        configVars['DJANGO_SETTINGS_MODULE'] = 'quant.django.settings.main'
        configVars['PYTHON_DEBUG'] = self.pythonDebugMode
        configVars['URI_PREFIX'] = self.noSlash(self.dictionary[URI_PREFIX])
        configVars['MEDIA_PREFIX'] = self.noSlash(self.dictionary[MEDIA_PREFIX])
        configVars['MEDIA_PATH'] = self.noSlash(self.dictionary[MEDIA_PATH])
        if self.dictionary[VIRTUALENVBIN_PATH]:
            configVars['HANDLER_PATH'] = 'quantvirtualenvhandlers::djangohandler'
        else:
            configVars['HANDLER_PATH'] = 'quant.handlers.modpython'

        # Assemble config content.
        configContent = """# Quant auto-generated Apache configuration.
"""
        # Assemble media config content.
        mediaConfigContent = ''
        if configVars['MEDIA_PREFIX']:
            mediaConfigContent = """            
# Media location.
Alias %(MEDIA_PREFIX)s/ %(MEDIA_PATH)s/
<Location "%(MEDIA_PREFIX)s/">
  SetHandler None
  Order Deny,Allow
  Allow from all
</Location>
            """ % configVars

        # Assemble app config content.
        if configVars['WSGI_SCRIPT_PATH']:
            # For Mod-WSGI.
            appConfigContent = """
# Application location.
WSGIScriptAlias %(WSGI_SCRIPT_ALIAS)s %(WSGI_SCRIPT_PATH)s 
""" % configVars
            configContent += mediaConfigContent + appConfigContent
        else:
            print "Warning: ModPython is deprecated. Instead, please set www.wsgi_file in system configuration file."
            # For Mod-Python.
            appConfigContent = """# %(SYSTEM_TITLE)s auto-generated Apache configuration.
# Application location.
<Location "%(URI_PREFIX)s/">
  SetEnv %(CONFIG_ENV_VAR_NAME)s %(SYSTEM_CONFIG_PATH)s
  SetEnv PYTHONPATH %(PYTHON_PATH)s
  SetEnv DJANGO_SETTINGS_MODULE %(DJANGO_SETTINGS_MODULE)s
  SetHandler python-program
  PythonPath "'%(PYTHON_PATH)s'.split(':') + sys.path"
  PythonHandler %(HANDLER_PATH)s
  PythonDebug %(PYTHON_DEBUG)s
</Location>
""" % configVars
            configContent += appConfigContent + mediaConfigContent
        return configContent

    def noSlash(self, path):
        if path and path[-1] == '/':
            path.pop()
        return path

    # Todo: Remove deprecated names.
    def buildConfig(self):
        "Deprected method name."
        self.buildConfigFile()

    def getConfig(self):
        "Deprecated method name."
        return self.createConfig()

    def buildWsgiFile(self):
        # Todo: Move this to filesystem object?
        wsgiScriptPath = self.dictionary[WSGI_SCRIPT_PATH]
        if not wsgiScriptPath:
            return
        wsgiFolderPath = os.path.dirname(wsgiScriptPath)
        wsgiScriptContent = self.createWsgiScriptContent()
        self.writeFile(wsgiScriptPath, wsgiScriptContent, '"WSGI file"')

    def createWsgiScriptContent(self):
        pythonVirtualenvActivation = ''
        pythonPathActivation = ''
        if self.dictionary[VIRTUALENVBIN_PATH]:
            pythonVirtualenvActivation = """
activate_this = '%(ACTIVATE_THIS_PATH)s'
execfile(activate_this, dict(__file__=activate_this))
"""         % {
                'ACTIVATE_THIS_PATH': os.path.join(self.dictionary[VIRTUALENVBIN_PATH], 'activate_this.py')
            }
        elif self.dictionary[PYTHONPATH]:
            pythonPathActivation = """
for path in %(PYTHON_PATH_LIST)s:
    if path not in sys.path:
        sys.path.append(path)
"""         % {
                'PYTHON_PATH_LIST': self.dictionary[PYTHONPATH].split(':'),
            }
        wsgiScriptBody = """import os
import sys

#############################################################
#
## %(SYSTEM_TITLE)s auto-generated WSGI File.
#
#############################################################

%(PYTHON_PATH_ACTIVATION)s

os.environ['DJANGO_SETTINGS_MODULE'] = '%(SYSTEM_PACKAGE_NAME)s.django.settings.main'
os.environ['%(CONFIG_ENV_VAR_NAME)s'] = '%(SYSTEM_CONFIG_PATH)s'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
"""     % {
            'SYSTEM_TITLE': self.dictionary[SYSTEM_TITLE],
            'SYSTEM_PACKAGE_NAME': self.dictionary[SYSTEM_PACKAGE_NAME],
            'CONFIG_ENV_VAR_NAME': self.environment.getConfigFilePathEnvironmentVariableName(),
            'SYSTEM_CONFIG_PATH': self.dictionary[SYSTEM_CONFIG_PATH],
            'PYTHON_VIRTUALENV_ACTIVATION': pythonVirtualenvActivation,
            'PYTHON_PATH_ACTIVATION': pythonPathActivation,
        }
        wsgiScriptContent = pythonVirtualenvActivation + wsgiScriptBody
        return wsgiScriptContent

