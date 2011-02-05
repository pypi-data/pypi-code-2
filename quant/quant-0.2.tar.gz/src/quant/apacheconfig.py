from dm.apache.config import ApacheConfigBuilder
from dm.ioc import RequiredFeature
from dm.dictionarywords import * 

class ApacheConfigBuilder(ApacheConfigBuilder):
    """
    Builds an Apache configuration for the Quant Web UI.
    """
    
    registry = RequiredFeature('DomainRegistry')
    fsPathBuilder = RequiredFeature('FileSystem')
    debug = RequiredFeature('Debug')
    
    def __init__(self):
        super(ApacheConfigBuilder, self).__init__()
    
    def noSlash(self, path):
        if path and path[-1] == '/':
            path.pop()
        return path

    def createConfigContent(self):
        configVars = {}
        configVars['CONFIG_ENV_VAR_NAME'] = self.environment.getConfigFilePathEnvironmentVariableName()
        configVars['SYSTEM_CONFIG_PATH'] = self.dictionary[SYSTEM_CONFIG_PATH]
        configVars['PYTHON_PATH'] = self.noSlash(self.dictionary[PYTHONPATH])
        configVars['DJANGO_SETTINGS_MODULE'] = 'quant.django.settings.main'
        if self.debug:
            configVars['PYTHON_DEBUG'] = 'On'
        else:
            configVars['PYTHON_DEBUG'] = 'Off'
        configVars['URI_PREFIX'] = self.noSlash(self.dictionary[URI_PREFIX])
        configVars['MEDIA_PREFIX'] = self.noSlash(self.dictionary[MEDIA_PREFIX])
        configVars['MEDIA_PATH'] = self.noSlash(self.dictionary[MEDIA_PATH])
        if self.dictionary[self.dictionary.words.VIRTUALENVBIN_PATH]:
            configVars['HANDLER_PATH'] = 'quantvirtualenvhandlers::djangohandler'
        else:
            configVars['HANDLER_PATH'] = 'quant.handlers.modpython'
        configContent = """# Quant auto-generated Apache configuration.
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
        
        if configVars['MEDIA_PREFIX']:
            configContent += """            
# Media location.
Alias %(MEDIA_PREFIX)s/ %(MEDIA_PATH)s/
<Location "%(MEDIA_PREFIX)s/">
  SetHandler None
  Order Deny,Allow
  Allow from all
</Location>
            """ % configVars
        return configContent

