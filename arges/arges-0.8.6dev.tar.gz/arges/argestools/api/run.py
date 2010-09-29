# -*- coding: latin-1 -*-

"""run - This module run the correct test according to the passed parameter 

@author Adrián Deccico
"""
import logging

class TestDispatcher:
    """this class will register commands and run inputs"""
    
    def __init__(self):
        #commands implemented by modules in this packages
        self.api = {}      
        
        #commands that are also run by modules in this packages but by using another objects
        #this is use in the case of Selenium commands which are run through the Selenium client
        #so this dictionary contains a group of other commands
        self.proxyApi = {}  
    
    def giveMeModuleName(self, module):
        #decide module name
        module_components = module.__name__.split(".")
        return module_components[len(module_components)-1]
        
    
    def registerCommand(self, module, command):
        """register new commands"""
        logging.debug("registering running module: " + module.__name__ + "  command: " + str(command))
        
        module_name = self.giveMeModuleName(module)
        
        #register command (or add it to the commands dictionay)
        #TODO: validate if the module exists in the dictionary
        self.api[module_name] = [module, command]
        logging.debug("command from running module: " + module.__name__ + " has been registered as " + module_name)
    
    def registerProxyCommand(self, module, runCommand, hasCommand):
        """register new proxy commands"""
        logging.debug("registering proxy module: " + module.__name__ + "  commands: " + str(runCommand) + " " + str(hasCommand))
        
        module_name = self.giveMeModuleName(module)
        
        #register command (or add it to the commands dictionay)
        #TODO: validate if the module exists in the dictionary
        self.proxyApi[module_name] = [hasCommand, runCommand]
        logging.debug("command from proxy module: " + module.__name__ + " has been registered as " + module_name)
        
    def run(self, args, parameters):
        #run the command against the correct function
        logging.info("running: " + str(args))
        
        ret = False
        commandExist = False
        
        if self.api.has_key(args[0]):
            #try to run the command in the registered api
            commandExist = True
            f = self.api[args[0]][1] #get function from dictionary
            ret = f(args[1], args[2], parameters) #execute function
        else:
            #or through a runProxied command 
            for cmd in self.proxyApi.keys():
                fHasFunction = self.proxyApi[cmd][0]
                if fHasFunction(args[0]):
                    commandExist = True
                    f = self.proxyApi[cmd][1] #get function from dictionary
                    ret = f(args[0], args[1], args[2], parameters) #execute function
                    break #if the function was found, then return the result 
                
        if not commandExist:
            logging.warning(str(args) + " does not exist in the registered api")
        return ret

