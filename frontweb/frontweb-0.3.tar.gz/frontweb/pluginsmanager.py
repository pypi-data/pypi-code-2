from yapsy.PluginManager import PluginManager
import os

def obtener_directorio_plugins():
    abspath = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(abspath, "plugins")

class PluginsManager:

    def __init__(self):
        self.manager = PluginManager(
                directories_list=[
                    obtener_directorio_plugins(),
                    ])
        self.manager.collectPlugins()

    def listar_plugins(self):
        return self.manager.getAllPlugins()
