# -*- coding: latin-1 -*-

"""testapi - is a package that provides an api to run any kind of generic test

This api, should be enough to test any kind of system, including server side commands 
and Web UI interfaces   

@author: Adrián Deccico
"""

import logging,sys
import run

#this attribute holds the run object which contains the api commands
#testDispatcher shpuld be the single attribute used externally to access to the 
#registerd api commands 
testDispatcher = run.TestDispatcher()   


#this list needs to be ensured in order to get the 
#sentence 'import *' working in all the platforms 
#TODO: decide if use this or the file list, or even better if a file is found
#        that do not match the uppercase name (the problem in windows) the file (module)
#        is add "as is"
__all__ = ["assertEqual", "commandLine", "commandLineRC", "createRandomFile", \
           "getMatchValue", "random_number_padding", "random_number", "readFile", \
           "remoteShell", "run", "seleniumWrapper", "setVar",  "wait"] 
           

#import all the modules
mods = [] #array of modules  
for module in __all__:
    mods.append(__import__(module, globals(), locals()))

#append possible non compatible modules (pexpect only works in unix-like systems)
other_modules = ["pexpectWrapper"]
for module in other_modules:
    try:
        mods.append(__import__(module, globals(), locals()))
        __all__.append(module)
    except:
        logging.debug(str(module) + " could not be imported. Probably is not compatible with this OS")




#iterate over all the modules and try to register the test api commands
#decide which module has register command and register it
runCommand = "runCommand"
runProxyCommand = "runProxiedCommand"
hasProxyCommand = "hasProxiedCommand"
for module in mods:
    #register a runCommand
    logging.debug("trying to register: " + str(module) + " to the api")
    
    try:
        f = getattr(module, runCommand)
        if callable(f):
            try:
                testDispatcher.registerCommand(module, f)
            except:
                logging.warning("problems registering module: " 
                                + module.__name__ + "  command: " + str(f))
                logging.exception("exception info:")
                continue
    except:
        pass #it is ok to not be able to register this command

    #register a runProxyCommand
    try:
        f = getattr(module, runProxyCommand)
        h = getattr(module, hasProxyCommand)
        if callable(f):
            try:
                testDispatcher.registerProxyCommand(module, f, h)
            except:
                logging.warning("problems registering module: " + module.__name__ 
                                + "  commands: " + str(f) + " and: " + str(h))
                logging.exception("exception info:")
                continue
    except:
        pass #it is ok to not be able to register this command 


logging.debug("finishing testapi __init__")
    
