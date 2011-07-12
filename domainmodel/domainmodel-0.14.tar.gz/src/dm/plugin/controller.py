import os, shutil

from dm.ioc import *
import dm.exceptions
from dm.dictionarywords import DB_MIGRATION_IN_PROGRESS

class PluginController(object):
    "Notifies plugins of core system events. 'Observer (293)' [GoF, 1995]"

    class __singletonPluginController(object):

        dictionary = RequiredFeature('SystemDictionary')
        registry = RequiredFeature('DomainRegistry')
        log = RequiredFeature('Logger')

        def __init__(self):
            self.plugins = None
    
        def notify(self, eventName, eventSender=None):
            "Notifies plugins of domain object events."
            msg = 'PluginController: Notifying plugins of ' 
            msg += '%s event from %s sender.' % (eventName, repr(eventSender))
            self.log.debug(msg)
            if eventName == 'PluginCreate':
                self.onPluginCreate(eventSender)
            if eventName == 'PluginDelete':
                self.onPluginDelete(eventSender)
            if self.dictionary[DB_MIGRATION_IN_PROGRESS]:
                return
            for plugin in self.getPlugins():
                eventReceiverName = 'on' + eventName
                if hasattr(plugin, eventReceiverName):
                    eventHandler = getattr(plugin, eventReceiverName)
                    if callable(eventHandler):
                        self.log.debug('PluginController: Notifying the %s plugin.' % plugin.domainObject.name)
                        eventHandler(eventSender)
        
        def onPluginCreate(self, pluginDomainObject):
            pluginSystem = pluginDomainObject.getSystem()
            if pluginSystem:
                pluginSystem.onCreate()
                self.getPlugins().append(pluginSystem)
        
        def onPluginDelete(self, pluginDomainObject):
            pluginSystem = pluginDomainObject.getSystem()
            if pluginSystem:
                pluginSystem.onDelete()
                self.getPlugins().remove(pluginSystem)
        
        def getPlugins(self):
            "Lazy-loads plugins."
            if self.plugins == None:
                self.plugins = []
                for plugin in self.registry.plugins:
                    pluginSystem = plugin.getSystem()
                    if not pluginSystem:
                        continue
                    self.plugins.append(pluginSystem)
            return self.plugins

    __instance = __singletonPluginController()

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)

