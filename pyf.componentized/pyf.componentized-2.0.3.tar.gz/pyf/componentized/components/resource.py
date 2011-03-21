from pkg_resources import iter_entry_points
from pyjon.utils.main import Singleton

import logging
logger = logging.getLogger()

class ResourceManager(object):
    
    plugin_types = [('adapter', 'adapters'),
                    ('producer', 'producers'),
                    ('consumer', 'consumers'),
                    ('joiner', 'joiners')]
    
    main_namespace = "pyf.components"
    
    __metaclass__ = Singleton
    
    def __init__(self):
        for type_name, subnamespace in self.plugin_types:
            setattr(self, 'get_%s' % type_name, self.get_plugin_getter(subnamespace))

    def __get_plugin(self, scope, name):
        """Return the plugin class with name on the scope
        """
        for entry_point in iter_entry_points(scope):
            try:
                plugin_class = entry_point.load()
                if plugin_class.name == name:
                    return plugin_class
            except Exception, e:
                logger.exception(e)

        raise ValueError('Plugin not found: %s.%s' % (scope, name))
    
    def get_plugin(self, plugin_type, plugin_name):
        plugin_namespace = "%s.%s" % (self.main_namespace, dict(self.plugin_types)[plugin_type])
        return self.__get_plugin(plugin_namespace, plugin_name)
        
    
    def get_plugins(self, plugin_type=None):
        if plugin_type:
            plugin_names = list()
            plugins = list()
            for entry_point in iter_entry_points("%s.%s" % (self.main_namespace,
                                                            plugin_type)):
                try:
                    plugin_class = entry_point.load()
                    if plugin_class.name in plugin_names:
                        logger.error('Two (or more) plugins with same entry point : %s.%s.%s' \
                                     % (self.main_namespace,
                                        plugin_type,
                                        plugin_class.name))
                    plugin_names.append(plugin_class.name)
                    plugins.append((plugin_class.name, plugin_class))
                except Exception, e:
                    logger.exception(e)
            return plugins
        else: 
            return dict([(pplugin_type, 
                          self.get_plugins(pplugin_type))
                         for splugin_type, pplugin_type in self.plugin_types])
            
    def get_plugin_getter(self, plugin_type_namespace):
        def plugin_getter(name):
            return self.__get_plugin("%s.%s" % (self.main_namespace, plugin_type_namespace),
                                     name)
        return plugin_getter