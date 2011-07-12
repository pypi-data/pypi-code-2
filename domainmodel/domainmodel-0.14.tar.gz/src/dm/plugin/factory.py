from dm.ioc import *
import dm.exceptions
from dm.plugin.base import PluginBase

class PluginFactory(object):

    dictionary = RequiredFeature('SystemDictionary')
    logger     = RequiredFeature('Logger')

    def getPlugin(self, domainObject):
        "Builds plugin system from plugin domain object."
        pluginName = domainObject.name
        pluginClass = self.getPluginClass(pluginName)
        if pluginClass:
            return pluginClass(domainObject)
        else:
            return None

    def getPluginClass(self, pluginName):
        pluginPackage = self.getPluginPackage(pluginName)
        pluginClass = None
        if pluginPackage:
            pluginPackageDict = pluginPackage.__dict__
            for value in pluginPackageDict.values():
                if type(value) == type and issubclass(value, PluginBase) \
                    and value.__module__.split('.')[-1] == pluginName:
                        if pluginClass:
                            msg = "Two plugin classes found in "
                            msg += "'%s' plugin module: " % pluginName
                            msg += "%s" % repr(pluginPackage)
                            raise dm.exceptions.MultiplePluginSystems(msg)
                        pluginClass = value
            if not pluginClass:
                msg = "Couldn't find a subclass of PluginBase in "
                msg += "'%s' plugin module: " % pluginName
                msg += "%s" % repr(pluginPackage)
                raise dm.exceptions.MissingPluginSystem(msg) 
        return pluginClass

    def getPluginPackage(self, pluginName):
        "Imports named plugin package."
        pluginPackageName = self.dictionary['plugin_package']
        pluginPackageName += '.' + pluginName
        try:
            pluginPackage = __import__(pluginPackageName, '', '', '*')
            if not pluginPackage:
                raise Exception("No plugin package was imported.")
        except Exception, inst:
            msg = "Could not import '%s' plugin package: %s." % (
                pluginPackageName, inst
            )
            self.logger.warn(msg)
            pluginPackage = None
        return pluginPackage

