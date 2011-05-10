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
    
    print config.security['code']
    
Special parameters:

-> lazy [default=False]
   Only load the configuration item on inital access.

-> live [default=False]
   Keeps the data in sync between the object and file. Do not use
   in a heavy load situation
   
-> skip [default=False]
   Do we raise an error when we cant load a YAML file or do we simply
   skip and ignore it.


UltraConfig is licensed under the MIT license.
"""
__author__  = "Jason Reid"
__version__ = "0.1"
__license__ = "MIT"

import os
import yaml

class UltraConfigException(Exception):
    pass
    
class UltraConfiguration(object):
    loaded = False

    def __init__(self, name, path, lazy=False, live=False):
        self.name = name
        self.path = path
        self.absolute = os.path.join(path, name+'.yml')
        self.mtime = 0
        self.data = None
        self.live = live
        self.lazy = lazy
        
        if not lazy:
            self.sync(force=True)
    
    def sync(self, force=False):
        if not self.in_sync() or force:
            self.load()

    def in_sync(self):
        if not self.loaded: return False

        if os.path.getmtime(self.absolute) > self.mtime:
            return False

        return 

    def load(self):
        self.mtime = os.path.getmtime(path)
        file = open(self.absolute, 'rb')
        self.data = yaml.load(file)
        file.close()
        self.loaded = True
    
    def __getitem__(self, name):
        if self.live: self.sync()
        return self.data[name]
        
    def __iter__(self):
        if self.live: self.sync()
        return self.data.__iter__()

class UltraConfig(object):  
    def __init__(self, profile, directory, lazy=False, live=False, skip=False):
        """ Pass in the name of the profile and the root directory
        where the configuration profiles are stored."""
        self.profile = profile
        self.directory = directory
        self.absolute = os.path.join(directory, profile)
        self.lazy = lazy
        self.live = live
        self.skip = skip

        self.configurations = {}
        self.broken = []

        # Do we automatically load?
        if not lazy:
            self.load_all()
    
    def sync(self):
        for configuration in self.configurations.items():
            configuration.sync()
        
    def reload(self, **options):
        """ Reload all the configurations """
        self.load(self.absolute, **options)

    def load_all(self):
        """ Load all the YAML files in the given directory."""
        if not os.path.isdir(self.absolute):
            raise UltraConfigException("Invalid directory: %s" % self.absolute)

        self.configurations = {}
            
        self.broken = []

        for item in os.listdir(self.absolute):
            if item.endswith('.yml'):
                path = os.path.join(self.absolute, item)
                name = item.replace('.yml','')
                try:
                    self.load_configuration(name)
                except yaml.YAMLError, e:
                    if self.skip:
                        self.broken.append(name)
                    else:
                        raise e

    def load_configuration(self, name):
        """ Load a specific YAML file into the configuration with the
        given name"""
        try:
            config = UltraConfiguration(name, self.absolute, self.lazy, self.live)
        except IOError, e:
            raise UltraConfigException("Could not open path %s because: %s" % (path, str(e)))
        else:
            self.configurations[name] = config
            
    def configuration_exists(self, name):
        return os.path.isfile(os.path.join(self.absolute, name+'.yml'))

    ## These are a series of special functions to allow easier access
    ## to the loaded configuration files.

    def __getattr__(self, name):
        if name in self.configurations:
            return self.configurations[name]
        if self.lazy and self.configuration_exists(name):
            try:
                self.load_configuration(name)
            except UltraConfigException, e:
                raise AttributeError(name)
            else:
                return self.configurations[name]
            
        raise AttributeError(name)
        
    def __hasattr__(self, name):
        return name in self.configurations or (self.lazy and configuration_exists(name))

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
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'testing')

    config1 = UltraConfig('profile1', path)
    config2 = UltraConfig('profile2', path)
    config3 = UltraConfig('profile3', path, lazy=True)
    try:
        config4 = UltraConfig('profile4', path)
    except yaml.YAMLError, e:
        assert isinstance(e,yaml.YAMLError)
    else:
        raise AssertionError("Did not get exception YAMLError!")
    
    try:
        config5 = UltraConfig('profile4', path, skip=True)
    except yaml.YAMLError, e:
        assert AssertionError("Got exception when not expected!")
    else:
        assert 'broken' not in config5 and 'security' in config5
        
    config6 = UltraConfig('profile1', path, lazy=True, live=True)
    
    try:
        print config6.super_secret
    except AttributeError, e:
        assert isinstance(e, AttributeError)
    else:
        raise AssertionError("Should have got attribute error for lazy config6.")

    assert config2
    assert hasattr(config1, 'caching') == True
    assert config1.caching['enabled'] == True
    assert config1.security['code'] == 654321
    assert config2.security['code'] == 123456
    assert config1.keys() == ['caching','security']

    # Test live read capabilities
    assert config6.security['code'] == 654321
    file = open(os.path.join(path, 'profile1', 'security.yml'), 'wb')
    file.write('code: 123456')
    file.close()

    assert config6.security['code'] == 123456
    file = open(os.path.join(path, 'profile1', 'security.yml'), 'wb')
    file.write('code: 654321')
    file.close()

    # Test hasitem capabilities
    assert 'security' in config1
    assert 'caching' not in config2
    assert 'security' not in config3
