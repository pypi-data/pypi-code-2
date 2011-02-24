from provide.plugin.base import ProvisionPlugin

class Plugin(ProvisionPlugin):

    def checkPluginDependencies(self):
        try:
            import sqlite
        except:
            msg = "Python package 'sqlite' can't be imported."

