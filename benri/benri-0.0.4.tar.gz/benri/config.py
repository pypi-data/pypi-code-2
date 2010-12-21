# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import os
from ConfigParser import SafeConfigParser

class ConfigFileMissing(Exception): pass
class RequiredAttrMissing(Exception): pass
class PathNotFound(Exception): pass

class Config(object):
    """
    Config-class that translates a config-file into a dictionary. A config-file
    conforms to the Python config-syntax:
    
    [section]
    attribute = value
    
    The config-dictionary is accessed with:
    config[section][attribute]
    
    Attributes not part of a section are ignored. There are also attributes 
    treated differently depending on their ending:
     
    '_path' - should be a path in the file-system, translated to an absolute path 
              and checked for existance. Raises PathNotFound-exception when the path
              does not exist.
    '_service' - Service-attributes represents a class handling WSGI-requests. The
                 config-dictionary will contain a list with all services.
                 
    - `configpath` - path to the configuration file
    - `basepath` - absolute path used as prefix for relative paths in the config
    - `required_attrs` - a list of (section, attribute)-tuples indicating that
                         the (section, attribute)-pair must exist
    """
    def __init__(self, configpath, workdir, required_attrs=[]):
        config = SafeConfigParser()
        
        if config.read([configpath]) == []:
            raise ConfigFileMissing("Configuration file: " + configpath + " not found")

        self.__data = {}
        
        for sec in config.sections():
            self.__data[sec] = {}
            
            for (item,value) in config.items(sec):
                if item.endswith('_path'):
                    if value.startswith('./'):
                        value = value[2:]
                    value = os.path.join(workdir, value)
                    
                    #if not os.path.exists(value):
                    #    raise PathNotFound(value)
                        
                #elif item.endswith('_service'):
                    # check if the value is a valid class-type
                    
                self.__data[sec][item] = value

        for (sec, attr) in required_attrs:
            try:
                self.__data[sec][attr]
            except KeyError, ke:
                raise RequiredAttrMissing('The required (section, attr)-pair could not be found: (%s, %s)' %(sec, attr))

    def __getitem__(self, key):
        return self.__data[key]

    def keys(self):
        return self.__data.keys()
        
# creates a Singleton-like object out of config
# better than passing around an instance to all
# objects that needs the values in the config-file.
#def Config(configpath, workdir):
#    return _Config(configpath, workdir)
    
