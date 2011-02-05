import os.path
from dm.ioc import *
from dm.dictionarywords import PLUGIN_DIR_PATH

class FileSystem(object):

    dictionary = RequiredFeature('SystemDictionary')
    logger = RequiredFeature('Logger')
    
    def getPluginsPath(self, plugin):
        if PLUGIN_DIR_PATH in self.dictionary:
            return self.dictionary[PLUGIN_DIR_PATH]
        else:
            # Todo: Config validation (since it's user input).
            msg = "Missing dictionary word. Try "
            msg += "setting '%s = /path/to/%s' in configuration." % (
                PLUGIN_DIR_PATH, PLUGIN_DIR_PATH
            )
            raise Exception, msg
    
    def getPluginPath(self, plugin):
        "Returns path of directory containing plugin filesystems."
        return os.path.join(self.getPluginsPath(), plugin.name)

# Old name.
class FileSystemPathBuilder(FileSystem):
    pass 
    

