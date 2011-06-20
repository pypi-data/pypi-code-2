# Todo: Figure out whether these tests have any value.

import kforge.soleInstance
import kforge.testunit
import kforge.plugin.factory

class TestFactory(kforge.testunit.TestCase):
    factory = kforge.plugin.factory.PluginFactory()

    def test_getEntryPoints(self):
        out = self.factory.getEntryPoints()
        names = [ x.name for x in out ]
        assert 'accesscontrol' in names
        assert 'apacheconfig' in names
    
    def test_getPluginClass(self):
        name = 'accesscontrol'
        plugin = self.factory.getPluginClass(name)
        assert plugin
        assert plugin.__name__ == 'Plugin'

    def test_getPlugin(self):
        # these plugins should be installed by default
        plugin1 = self.registry.plugins['accesscontrol']
        plugin2 = self.registry.plugins['apacheconfig']

        plugin_system = self.factory.getPlugin(plugin1)
        assert plugin_system
        assert plugin_system.__class__.__name__ == 'Plugin'
        plugin_system = self.factory.getPlugin(plugin2)
        assert plugin_system

