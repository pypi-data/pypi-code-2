import dm.plugin.factory

# TODO: appears that this is only used from dom.plugin.Plugin.getSystem()
# so could replace there and get rid of this altogether ...
# (in dm also used from dm.command.plugin but that is not used I think ...)

# Todo: Make this a KForge error.
class MissingPluginEntryPoint(Exception): pass

class PluginFactory(dm.plugin.factory.PluginFactory):

    def getPluginClass(self, name):
        pluginClass = super(PluginFactory, self).getPluginClass(name)
        if not pluginClass:
            try:
                entrypoint = self.getEntryPoint(name)
            except MissingPluginEntryPoint, inst:
                msg = "Could not find a setuptools entry point"
                msg += " for '%s' plugin: %s" % (name, str(inst))
                self.logger.warn(msg)
                pluginClass = None
            else:
                try:
                    pluginClass = entrypoint.load()
                except Exception, inst:
                    msg = "Could not load setuptools entry point"
                    msg += " for '%s' plugin." % name # No point using the inst
                    # string because it is misleading (refers to Django).
                    #msg += " for '%s' plugin: %s" % (name, str(inst))
                    self.logger.error(msg)
                    pluginClass = None
        return pluginClass

    def getEntryPoint(self, name):
        import pkg_resources
        for entrypoint in pkg_resources.iter_entry_points('kforge.plugins'):
            if entrypoint.name == name:
                return entrypoint
        msg = 'No entry point found for plugin: %s' % name
        raise MissingPluginEntryPoint(msg)

    def getEntryPoints(self):
        import pkg_resources
        entrypoints = []
        for en in pkg_resources.iter_entry_points('kforge.plugins'):
            entrypoints.append(en)
        return entrypoints
