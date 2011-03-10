"""
Helper logic for reading and writing configuration files.
"""

from ConfigParser import SafeConfigParser
import os


def InitConfigFile(dataPath, configFileName, defaults=()):
    """
    This takes care of three aspects of reading a .ini configuration file:

     #. Read in a configuration file if it exists.
     #. Take the set of default values specified by :literal:`defaults` and
        ensure any missing values are populated from it.  If the configuration
        file did not exist, all the default values will be populated.
     #. Write out the updated configuration file.
    """
    config = ReadConfigFile(dataPath, configFileName, defaults)
    WriteConfigFile(dataPath, configFileName, config)
    return config

def ReadConfigFile(dataPath, configFileName, defaults=()):
    """
    This takes care of two aspects of reading a configuration file:

     #. Read in a configuration file if it exists.
     #. Take the set of default values specified by :literal:`defaults` and
        ensure any missing values are populated from it.  If the configuration
        file did not exist, all the default values will be populated.
    """
    config = SafeConfigParser()
    configFilePath = os.path.join(dataPath, configFileName)

    if os.path.exists(configFilePath):
        f = open(configFilePath, "r")
        config.readfp(f)

    for sectionName, variableName, variableValue in defaults:
        if not config.has_section(sectionName):
            config.add_section(sectionName)
        if not config.has_option(sectionName, variableName):
            config.set(sectionName, variableName, str(variableValue))

    return config

def WriteConfigFile(dataPath, configFileName, config):
    """
    Simply write out the configuration :literal:`config` to the given location.
    """
    configFilePath = os.path.join(dataPath, configFileName)
    f = open(configFilePath, "w")
    config.write(f)
