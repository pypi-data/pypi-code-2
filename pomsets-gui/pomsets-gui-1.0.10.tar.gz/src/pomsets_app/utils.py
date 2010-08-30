from __future__ import with_statement

import simplejson as ConfigModule
import os
import pickle
import time
import tarfile
import user


def getDefaultConfigDir():
    # wx.StandardPaths.Get().GetUserDataDir() 
    # Return the directory for the user-dependent application data files: 
    # $HOME/.appname under Unix, 
    # c:/Documents and Settings/username/Application Data/appname under Windows and 
    # ~/Library/Application Support/appname under Mac

    # for now, we just use $HOME/.pomsets
    configDir = os.path.join(user.home, '.pomsets')
    return configDir


def getDefaultConfigPath(configDir=None):

    if configDir is None:
        configDir = getDefaultConfigDir()

    configPath = os.path.join(configDir, 'config')
    
    return configPath


def saveConfig(configData, configPath=None):

    # this is the default path
    if configPath is None:
        configPath = getDefaultConfigPath()

    with open(configPath, 'w') as f:
        ConfigModule.dump(configData, f, sort_keys=True, indent=4)
        pass
    return


def loadConfig(configPath=None):

    # this is the default path
    if configPath is None:
        configPath = getDefaultConfigPath()

    with open(configPath) as f:
        config = ConfigModule.load(f)
        return config

    raise IOError('could not read load config from config path %s' % configPath)


def createNewConfigDataObject():
    return {}


def backupLibrary(libraryDir, destination=None):

    if destination is None:
        destination = libraryDir + "." + str(int(time.time())) + ".tgz"
        
    tarball = tarfile.open(name=destination, mode='w:gz')
    tarball.add(libraryDir, arcname="library")
    tarball.close()

    return destination
