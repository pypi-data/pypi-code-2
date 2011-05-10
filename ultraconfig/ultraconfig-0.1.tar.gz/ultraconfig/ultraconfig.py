"""
UltraConfig is an easy to use library that can load an entire folder's
worth of YAML configuration files. This is useful for adding profile
specific configuration to an application.

The directory structure of a configuration directory should be as follows:
    my_application/
        configuration/
            development/
                database.yml
                caching.yml
                security.yml
            production/
                database.yml
                caching.yml
                security.yml
    
Using the UltraConfig is relatively simple:
    config = UltraConfig('development', '/my_application/configuration/')
    
    print config.security['secret_key']
    print config['security']['secret_key']

UltraConfig is licensed under the MIT license.
"""
__author__  = "Jason Reid"
__version__ = "0.1"
__license__ = "MIT"

import os
import yaml

class UltraConfigException(Exception):
    pass

class UltraConfig(object):  
    def __init__(self, profile, directory, autoload=True, **options):
        """ Pass in the name of the profile and the root directory
        where the configuration profiles are stored."""
        self.profile = profile
        self.directory = directory
        self.absolute = os.path.join(directory, profile)

        # This is not used yet.
        self.options = options

        self.configurations = {}
        self.broken = []

        # Do we automatically load?
        if autoload:
            self.load(self.absolute, **self.options)

    def reload(self, **options):
        """ Reload all the configurations """
        self.load(self.absolute, **options)

    def load(self, directory, reset=True, override=True, skipbroken=False):
        """ Load all the YAML files in the given directory."""
        if not os.path.isdir(directory):
            raise UltraConfigException("Invalid directory: %s" % directory)

        if reset:
            self.configurations = {}
            
        self.broken = []

        for item in os.listdir(directory):
            if item.endswith('.yml'):
                path = os.path.join(directory, item)
                name = item.replace('.yml','')
                if name not in self.configurations or override:
                    try:
                        self.load_configuration(name, path)
                    except yaml.YAMLError, e:
                        if skipbroken:
                            self.broken.append(name)
                        else:
                            raise e

    def load_configuration(self, name, path):
        """ Load a specific YAML file into the configuration with the
        given name"""
        try:
            file = open(path, "rb")
        except IOError, e:
            raise UltraConfigException("Could not open path %s because: %s" % (path, str(e)))
        else:
            config = yaml.load(file)
            file.close()
            self.configurations[name] = config

    ## These are a series of special functions to allow easier access
    ## to the loaded configuration files.

    def __getattr__(self, name):
        if name in self.configurations:
            return self.configurations[name]
        raise AttributeError(name)
        
    def __hasattr__(self, name):
        return name in self.configurations

    def __getitem__(self, name):
        return self.configurations[name]

    def __setitem__(self, name, config):
        self.configurations[name] = config

    def __iter__(self):
        return self.configurations.__iter__()

    def items(self):
        return self.configurations.items()

    def keys(self):
        return self.configurations.keys()

    def iteritems(self):
        return self.configurations.iteritems()

if __name__ == "__main__":
    # Some random simple testing
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'testing')

    config1 = UltraConfig('profile1', path)
    config2 = UltraConfig('profile2', path)
    config3 = UltraConfig('profile3', path, autoload=False)
    try:
        config4 = UltraConfig('profile4', path)
        print config4.items()
    except yaml.YAMLError, e:
        assert isinstance(e,yaml.YAMLError)
    else:
        raise AssertionError("Did not get exception YAMLError!")
    
    try:
        config5 = UltraConfig('profile4', path, skipbroken=True)
    except yaml.YAMLError, e:
        assert AssertionError("Got exception when not expected!")
    else:
        assert 'broken' not in config5 and 'security' in config5

    assert config2
    assert hasattr(config1, 'caching') == True
    assert config1.caching['enabled'] == True
    assert config1.security['code'] == 654321
    assert config2.security['code'] == 123456
    assert config2['security']['code'] == 123456
    assert config1.keys() == ['caching','security']
    assert 'security' in config1
    assert 'caching' not in config2
    assert 'security' not in config3
