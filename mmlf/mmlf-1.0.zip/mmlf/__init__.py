# Maja Machine Learning Framework
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

""" Maja Machine Learning Framework

The Maja Machine Learning Framework (MMLF) is a general framework for 
problems in the domain of Reinforcement Learning (RL). It provides a 
set of RL related algorithms and a set of benchmark domains. 
Furthermore it is easily extensible and allows to automate 
benchmarking of different agents. 

Among the RL algorithms are TD(lambda), DYNA-TD, CMA-ES,
Fitted R-Max, and Monte-Carlo learning. MMLF contains different 
variants of the maze-world and pole-balancing problem class as 
well as the mountain-car testbed.

Further documentation is available under http://mmlf.sourceforge.net/

Contact the mailing list MMLF-support@lists.sourceforge.net
if you have any questions.
"""

__author__ = "Jan Hendrik Metzen"
__copyright__ = "Copyright 2011, University Bremen, AG Robotics"
__credits__ = ['Mark Edgington']
__license__ = "GPLv3"
__version__ = "1.0"
__maintainer__ = "Jan Hendrik Metzen"
__email__ = "jhm@informatik.uni-bremen.de"


import sys
import os
import shutil
import time
import warnings
import yaml
import glob

import framework.mmlf_logging
log = framework.mmlf_logging.getLogger('FrameworkLog')

if not "HOME" in os.environ and "USERPROFILE" in os.environ: # MS Windows
    os.environ["HOME"] = os.environ["USERPROFILE"]
    
def setupConsoleLogging(*args, **kwargs):
    framework.mmlf_logging.setupConsoleLogging(*args, **kwargs)

def setupFileLogging(*args, **kwargs):
    framework.mmlf_logging.setupFileLogging(*args, **kwargs)

def initializeRWArea(rwPath=None):
    """ Initialize the RW area.
    
    If *rwPath* is specified, the RW area located under that path is used.
    Otherwise, the standard RW area under ~./mmlf is used.
    
    If the required RW area does not exist, it is automatically created under
    the specified path.
    """
    def createRWArea(rwPath):
        # Helper function that creates the RW area under the guven path
        if not os.path.exists(rwPath):
            os.makedirs(rwPath)
        os.makedirs(rwPath + os.sep +  "logs")
        # Copy config files from RO area to RW area
        if os.path.exists("config"):
            shutil.copytree("config", rwPath + os.sep +  "config")
        else:
            if sys.platform == 'win32':
                shutil.copytree("%s\\mmlf\\config" % os.environ["APPDATA"], 
                                rwPath + os.sep +  "config")
            elif sys.platform in ['darwin', 'linux2']:
                shutil.copytree("/etc/mmlf/config", 
                                rwPath + os.sep +  "config")
    
    if rwPath is not None:
        assert os.path.isabs(rwPath), \
                "Path to RW area must be absolute, not '%s'." % rwPath
        # Set environment variable pointing to the MMLF RW directory
        os.environ["MMLF_RW_PATH"] = rwPath
        log.info("Using MMLF RW area %s" % os.environ["MMLF_RW_PATH"])
        if not os.path.exists(rwPath):
            createRWArea(rwPath)
    else:
        mmlfRWArea = os.environ.get("HOME") + os.sep + ".mmlf"
        # Set environment variable pointing to the MMLF RW directory
        os.environ["MMLF_RW_PATH"] = mmlfRWArea
        if not os.path.exists(mmlfRWArea):
            createRWArea(mmlfRWArea)
        
    log.info("Using MMLF RW area %s" % os.environ["MMLF_RW_PATH"])
    
def getRWPath():
    """ Return the RW path to be used. """
    default = '/tmp' if sys.platform != 'win32' else "C:\Temp"    
    return os.environ.get("MMLF_RW_PATH", default)

def loadWorldFromConfigFile(configPath, useGUI):
    """ Load the world specified in the *configPath*."""
    from mmlf.framework.filesystem import BaseUserDirectory
    from mmlf.framework.world import World
    
    # Create base user directory
    baseUserDir = BaseUserDirectory()
    
    # Set worldConfigFile and create a ConfigWrapper object from it
    if not os.path.isabs(configPath):
        absConfigPath = baseUserDir.getAbsolutePath("rwconfig", configPath)
        if not os.path.exists(absConfigPath):
            # Fall back to ro area
            absConfigPath = baseUserDir.getAbsolutePath("roconfig", configPath)
            if not os.path.exists(absConfigPath):
                raise UserWarning("Can't find the config file %s" % configPath)
    else:
        absConfigPath = configPath
    
    worldConfigObject = yaml.load(open(absConfigPath, 'r'))
                       
    return loadWorld(worldConfigObject, baseUserDir, useGUI=useGUI)
    

def loadWorld(worldConfigObject, baseUserDir=None, useGUI=False, 
              keepObservers=[]):
    """ Load the world specified in the *worldConfigObject*."""
    from mmlf.framework.filesystem import BaseUserDirectory
    from mmlf.framework.world import World
    
    if baseUserDir == None:
        baseUserDir = BaseUserDirectory()
    
    # OBSERVABLES must contain only observables of type AllObservables and 
    # AllViewers when starting a world. Other observables are from prior runs 
    # and are deleted
    from mmlf.framework.observables import OBSERVABLES, AllObservables
    from mmlf.gui.viewers import AllViewers
    cleanedListOfObservables = []
    for observable in OBSERVABLES.allObservables:
        if not (isinstance(observable, AllObservables) 
                  or isinstance(observable, AllViewers)):
            del(observable)
        else:
            observable.observers = filter(lambda o: o in keepObservers,
                                          observable.observers)
            cleanedListOfObservables.append(observable)
    OBSERVABLES.allObservables = cleanedListOfObservables
        
    return World(worldConfigObject, baseUserDir, useGUI) 
    

def loadExperimentConfig(experimentPath):
    """ Load the specification of an MMLF experiment into a dict."""
    if not os.path.isabs(experimentPath):
        # Assume it is relative to root of MMLF RW-directory
        experimentPath = getRWPath() + os.sep + experimentPath
        
    experimentConfigFile = experimentPath + os.sep + "experiment_config.yaml"
    experimentConf = yaml.load(open(experimentConfigFile, 'r'))
        
    # Add all worlds specified in this directory to the world list
    experimentConf["worlds"] = dict()
    worldDir = experimentPath + os.sep + "worlds"
    for worldConfFile in glob.glob(worldDir + os.sep + "*.yaml"):
        worldConfigObject = yaml.load(open(worldConfFile, 'r'))
        worldName = worldConfFile.split(os.sep)[-1][:-5]
        experimentConf["worlds"][worldName] = worldConfigObject 
        
    return experimentConf

def runExperiment(experimentConf):
    """ Execute an experiment."""
    # Creating queues for inter-process communication
    from multiprocessing import Queue
    observableQueue = Queue()
    updateQueue = Queue()
    
    # Run the experiment in a separate thread
    from mmlf.framework.experiment import runExperiment
    from threading import Thread
    launcherThread = Thread(target=runExperiment, 
                            args=(experimentConf, observableQueue, 
                                  updateQueue, None))
    launcherThread.start()
    
    # Keep getting items from queues such that subprocesses can terminate
    while launcherThread.is_alive():
        try:
            observableQueue.get(False)
        except:
            pass
        try:
            updateQueue.get(False)
        except:
            pass
    
