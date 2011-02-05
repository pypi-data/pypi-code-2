import dm
from dm.config import ConfigFileReader
import os
import dm.dictionarywords
from dm.dictionarywords import *
from dm.environment import SystemEnvironment
import dm.times
from dm.exceptions import InvalidSystemDictionary, MissingConfigurationPath

# Todo: Check Django settings has DEFAULT_CHARSET == 'utf-8'.

class SystemDictionary(dict):
    "Dictionary of system attributes."

    words = dm.dictionarywords 

    def __init__(self):
        super(SystemDictionary, self).__init__()
        self.assertSystemName()
        self.environment = SystemEnvironment(self.getSystemName())
        self.assertSystemEnvironment()
        self.setDefaultWords()
        self.makeConfigFilePath()
        self.assertConfigFileExists()
        self.makeConfigFileReader()
        self.initConfigFileReader()
        self.readConfigFile()  # Todo: Validate configuration file items.
        self.setWordsFromConfigFile()
        self.setWordsFromWords()
        self.setConfigFilePathWord()
        self.setNewWordsFromOld()
        self.initTimezone()
        self.setSystemUpSince()
        self.validateDictionaryWords()
        self.assertWebkitEnvironment()

    def assertSystemName(self):
        if not self.getSystemName():
            raise Exception, "No system name!"
        
    def assertSystemEnvironment(self):
        pass

    def assertWebkitEnvironment(self):
        if self[WEBKIT_NAME] == 'django':
            self.environment.assertDjangoSettingsModule()
        
    def setDefaultWords(self):
        self[PYTHONPATH]          = '' #os.environ.get('PYTHONPATH', '')
        self[SYSTEM_NAME]         = self.getSystemName()
        self[SYSTEM_PACKAGE_NAME] = self.getSystemPackageName()
        self[SYSTEM_SERVICE_NAME] = self.getSystemServiceName()
        self[SYSTEM_MODE]         = 'production'
        self[SYSTEM_VERSION]      = self.getSystemVersion()
        self[VISITOR_NAME]        = 'visitor'
        self[VISITOR_ROLE]        = 'Visitor'
        self[INITIAL_PERSON_ROLE] = 'Visitor'
        self[PLUGIN_PACKAGE_NAME] = 'dm.plugin'
        self[CAPTCHA_IS_ENABLED]  = '' # False (ConfigParser only supports str)
        self[AUTH_COOKIE_NAME]    = '%s_auth' % self[SYSTEM_NAME]
        self[NO_AUTH_COOKIE_NAME] = '%s_no_auth' % self[SYSTEM_NAME]
        self[LOG_PATH]            = ''
        self[LOG_LEVEL]           = 'ERROR'
        self[APACHE_IP_ADDRESS]   = '*'
        self[APACHE_CONFIG_PATH]  = ''
        self[APACHE_RELOAD_CMD]   = '' #'sudo /etc/init.d/apache2 reload'
        self[SKIP_APACHE_RELOAD]  = ''
        self[APACHE_CONFIGTEST_CMD] = '' #'sudo /etc/init.d/apache2 configtest'
        self[DOMAIN_NAME]         = self.getDomainName()
        self[HTTP_PORT]           = '80'
        self[HTTPS_PORT]          = '443'
        self[URI_PREFIX]          = ''
        self[MEDIA_PATH]          = ''
        self[MEDIA_HOST]          = ''
        self[MEDIA_PORT]          = '' 
        self[MEDIA_PREFIX]        = '/media'
        # For values of the TIMEZONE word, please read the information
        # about the TZ environment variable in this tzset() reference:
        #     http://docs.python.org/lib/module-time.html
        self[TIMEZONE]            = '' # Defaults to unchanged environment.
        self[SERVICE_EMAIL]       = ''
        self[SMTP_HOST]           = ''
        self[SKIP_EMAIL_SENDING]  = ''
        self[EMAIL_NOTIFY_CHANGES]= ''
        self[IMAGES_DIR_PATH]     = ''
        # Potential values: 'mysql', 'postgres', 'sqlite', 'firebird', 'sybase', 'maxdb', 'mssql'.
        self[DB_TYPE]             = 'postgres' 
        self[DB_HOST]             = 'localhost'
        self[DB_NAME]             = self[SYSTEM_NAME]
        self[DB_USER]             = self[DB_NAME]
        self[DB_PASS]             = ''
        self[DB_SUPER_USER]       = ''
        self[DB_SUPER_PASS]       = ''
        self[DB_CREATE_COMMAND]   = ''  # Default depends on DB_TYPE.
        self[DB_DELETE_COMMAND]   = ''  # Default depends on DB_TYPE.
        self[DB_MIGRATION_IN_PROGRESS] = ''
        self[DJANGO_SECRET_KEY]   = 'not-a-secret'
        self[DJANGO_TEMPLATES_DIR] = ''
        self[EDITOR]              = 'editor' # Debian specific...
        self[WEBKIT_NAME] = 'django' # No value other than 'django' supported.
        self[VIRTUALENVBIN_PATH]  = ''
        self[MEMOS_LIMIT]         = '3000'
        self[MEMOS_EXPIRE]        = '30'
        self[MEMOS_ENABLED]       = ''
        self[TEMPLATES_RESOURCE_PATH] = 'django/templates'
        self[MEDIA_RESOURCE_PATH] = 'django/media'

    def makeConfigFilePath(self):
        self.configFilePath = self.environment.getConfigFilePath().strip()
        if not self.configFilePath:
            raise MissingConfigurationPath("No configuration file path has been provided (export %s=/path/to/kforge.conf in the operating environment)." % self.environment.getConfigFilePathEnvironmentVariableName())

    def setConfigFilePathWord(self):
        self[SYSTEM_CONFIG_PATH] = self.configFilePath

    def assertConfigFileExists(self):
        if not os.path.isfile(self.configFilePath):
            raise Exception("Configuration file not found on path: %s" % self.configFilePath)

    def makeConfigFileReader(self):
        self.configFileReader = ConfigFileReader()
        
    def initConfigFileReader(self):
        for key in self.keys():
            self.configFileReader[key] = self[key]
        
    def readConfigFile(self):
        pathList = [self.configFilePath]
        try:
            self.configFileReader.read(pathList)
        except Exception, inst:
            msg = "Couldn't read configuration file: %s" % str(inst)
            raise Exception, msg
        
    def setWordsFromConfigFile(self):
        configWords = self.configFileReader.keys()
        for configWord in configWords:
            configValue = self.configFileReader[configWord]
            # Todo: Interestingly, converting all dict values to 
            # unicode breaks things quite a lot. Find out why!
            #if type(configValue) == str:
                #configValue = configValue.decode('utf-8')
                #print "%s %s" % (configWord, repr(configValue))
            self[configWord] = configValue
        if self[LOG_PATH] == '':
            raise Exception("No path for logging has been provided. Try setting '%s' in the configuration file: %s" % (LOG_PATH, self.configFilePath))

    def setWordsFromWords(self):
        # Media host and post.
        #if not self[MEDIA_HOST]:
        #    self[MEDIA_HOST] = self[DOMAIN_NAME]
        if not self[MEDIA_PORT]:
            self[MEDIA_PORT] = self[HTTP_PORT]
        # Database super user.
        if not self[DB_SUPER_USER]:
            self[DB_SUPER_USER] = self[DB_USER]
        if not self[DB_SUPER_PASS]:
            self[DB_SUPER_PASS] = self[DB_PASS]
        # Database create and delete commands.
        dbCmds = {
          'postgres': {
            'create': "createdb -h %(host)s -U %(super_user)s %(name)s",
            'delete': "dropdb -h %(host)s -U %(super_user)s %(name)s",
          },
          'mysql': {
            'create': "mysqladmin -h'%(host)s' -u'%(super_user)s' -p'%(super_pass)s' create %(name)s",
            'delete': "mysqladmin -h'%(host)s' -u'%(super_user)s' -p'%(super_pass)s' --force drop %(name)s",
          },
          'sqlite': {
            'create': "touch %(name)s",
            'delete': "rm %(name)s",
          },
        }
        dbVars = {
          'name': self[DB_NAME],
          'user': self[DB_USER],
          'pass': self[DB_PASS],
          'host': self[DB_HOST],
          'super_user': self[DB_SUPER_USER],
          'super_pass': self[DB_SUPER_PASS],
        }
        if not self[DB_CREATE_COMMAND]:
            if self[DB_TYPE] in dbCmds:
                try:
                    cmd = dbCmds[self[DB_TYPE]]['create'] % dbVars
                except:
                    msg = "Couldn't generate %s database create command. Commands: %s Vars: %s" % (self[DB_TYPE], dbCmds, dbVars)
                self[DB_CREATE_COMMAND] = cmd
            else:
                msg = "Inferring database create command for database type"
                msg += " '%s' not supported." % self[DB_TYPE]
                msg += " Try setting 'create_command = ...' in the [db]"
                msg += " section of the configuration file."
                raise Exception, msg
        if not self[DB_DELETE_COMMAND]:
            if self[DB_TYPE] in dbCmds:
                try:
                    cmd = dbCmds[self[DB_TYPE]]['delete'] % dbVars
                except:
                    msg = "Couldn't generate %s database delete command. Commands: %s Vars: %s" % (self[DB_TYPE], dbCmds, dbVars)
                self[DB_DELETE_COMMAND] = cmd
            else:
                msg = "Inferring database delete command for database type"
                msg += " '%s' not supported." % self[DB_TYPE]
                msg += " Try setting 'delete_command = ...' in the [db]"
                msg += " section of the configuration file."
                raise Exception, msg
        if PYTHONPATH_ALT in self:
            if not self[PYTHONPATH]:
                self[PYTHONPATH] = self.pop(PYTHONPATH_ALT)
        if self[VIRTUALENVBIN_PATH]:
            if self[PYTHONPATH]:
                self[PYTHONPATH] = self[VIRTUALENVBIN_PATH]+":"+self[PYTHONPATH]
            else:
                self[PYTHONPATH] = self[VIRTUALENVBIN_PATH]
            
    def setNewWordsFromOld(self):
        # Support usage of old dictionary words in existing config files.
        if OLD_DB_PASS in self:
            # Todo: Warn of deprecation.
            if not self[DB_PASS]:
                self[DB_PASS] = self.pop(OLD_DB_PASS)
        if OLD_MEDIA_PATH in self:
            # Todo: Warn of deprecation.
            if not self[MEDIA_PATH]:
                self[MEDIA_PATH] = self.pop(OLD_MEDIA_PATH)
    
    def getSystemVersion(self):
        return dm.__version__

    def getSystemName(self):
        return 'domainmodel'

    def getSystemPackageName(self):
        systemName = self.getSystemName()
        if systemName == 'domainmodel':
            packageName = 'dm'
        else:
            packageName = systemName
        return packageName

    def getSystemServiceName(self):
        return self.getSystemName().capitalize()

    def getDomainName(self):
        # Todo: This is used for sending mail, doesn't help with Web UI, so move to 'MAIL_DOMAIN'?
        import platform
        return platform.node()

    def initTimezone(self):
        if self[TIMEZONE]:
            self.environment.setTimezone(self[TIMEZONE])
            dm.times.resetTimezone()

    def setSystemUpSince(self):
        self.set(SYSTEM_UP_SINCE, dm.times.getUniversalNow()) 

    def set(self, name, value):
        self[name] = value

    def validateDictionaryWords(self):
        self.validateUriPrefix()
        # todo: More dictionary word validation.

    def validateUriPrefix(self):
        uriPrefix = self[URI_PREFIX]
        if uriPrefix == '':
            return
        if uriPrefix[0] != '/':
            msg = "No leading slash on '%s': '%s'." % (
                URI_PREFIX, self[URI_PREFIX]
            )
            raise InvalidSystemDictionary(msg)
        if uriPrefix[-1] == '/':
            msg = "Trainling slash on '%s': '%s'." % (
                URI_PREFIX, self[URI_PREFIX]
            )
            raise InvalidSystemDictionary(msg)
        


