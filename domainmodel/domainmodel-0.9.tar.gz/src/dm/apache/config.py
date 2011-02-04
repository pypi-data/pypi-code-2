from dm.ioc import RequiredFeature
from dm.dictionarywords import SYSTEM_NAME, SYSTEM_MODE
from dm.dictionarywords import APACHE_RELOAD_CMD, SKIP_APACHE_RELOAD
from dm.dictionarywords import APACHE_CONFIG_PATH
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
        configPath = os.path.normpath(configPath)
        configPathParent = os.path.dirname(configPath)
        if not os.path.exists(configPathParent):
            os.makedirs(configPathParent)
        configContent = configContent.encode('utf-8', 'ignore')
        # Todo: Make this filewriting safer.
        file = open(configPath, 'w')
        file.write(configContent)
        file.close()
        self.logger.info("%s: Written new apache config to path: %s" % (self.__class__.__name__, configPath))

    def createConfigContent(self):
        return ""

    # Todo: Remove deprecated names.
    def buildConfig(self):
        "Deprected method name."
        self.buildConfigFile()

    def getConfig(self):
        "Deprecated method name."
        return self.createConfig()


