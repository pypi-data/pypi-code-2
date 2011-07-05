import yaml

#try:
#    from yaml import CLoader as Loader
#    from yaml import CDumper as Dumper
#except ImportError:
#    from yaml import Loader, Dumper

class YamlSettingsProvider(object):
    def load(self, serialized_settings):
        """
        Should return json-like dictionary of settings
        """
        return yaml.load(serialized_settings)

    def dump(self, settings):
        return yaml.dump(settings, default_flow_style=False)
