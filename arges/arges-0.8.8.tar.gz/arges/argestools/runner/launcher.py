# -*- coding: latin-1 -*-

"""launcher - Launcher module, useful to run test files

@author: Adrián Deccico
"""

import re
import logging

import arges.argestools.api
import arges.argestools.argesfiles
import arges.util

class Launcher:
    """ This class encapsulates launching logic for other resources
    """
    
    def __init__(self, steps, parameters = {}):
        #constants
        self.COMMAND_COL = 0
        self.TARGET_COL = 1
        self.VALUE_COL = 2
        self.RETVAR_COL = 3       #return variable column. This column is used to get the result of a step and set a parameter
        self.CRITICITY_COL = 4    #the criticity of the step
        self.DESCRIPTION_COL = 5  #the description of the step  

        self.steps = steps #steps to be run
        self.runner = arges.argestools.api.testDispatcher  #the runner who will provide the api

        #a cache that will store the parameters set or got by the steps. 
        #The parameters will be valid regex expressions
        self.parameters = parameters    
        self.cols_with_parameters_to_be_replaced = [self.COMMAND_COL, self.TARGET_COL, self.VALUE_COL]

        #function transformation dict
        self.FUNCTION_TRANSFROMATION = {"":"setVar"}

    
    def setParametersInTheStep(self, step):
        """replace in each step a parameter ${ANY} for its parameters"""
        for key in self.parameters.keys():
            for i in self.cols_with_parameters_to_be_replaced:
                try:
                    if step[i] != None:
                        step[i] = re.sub(key, self.parameters[key], step[i])
                except:
                    logging.error("problems setting parameters with this step: " + str(step))
                    logging.exception("exception info:")
                            
    def isFatal(self, step_value):
        """evaluate the criticity of a step"""
        step_value = arges.util.strings.trim(step_value) if step_value != None else None
        if step_value != None and step_value.upper() == "WARNING":
            return False
        else:
            return True
    
    def run(self, closeWindows=False): #run the list of commands. Return the number of processed commands
        number_of_results = 0
        parseFile = arges.argestools.argesfiles.parsefile.ParseFile()
        
        try:
            for line_number, test_step in enumerate(self.steps):
                logging.debug("sending command: " + str(test_step))
                
                #get criticity. By default is fatal
                isFatal = self.isFatal(test_step[self.CRITICITY_COL])
                logging.debug("is fatal (or should the execution stopped if this command fail) ? " + str(isFatal))
                
                #save the parameter as long as is mutable and test_step could possible be changed
                retvar = test_step[self.RETVAR_COL] 
                
                #validate retvar
                if retvar != None and not parseFile.isValidParameter(retvar) :
                    msg = "Test step number: " + str(line_number) + " - " + str(test_step) + " " 
                    msg = msg + str(retvar) + " is an invalid return parameter. Should be something like ${PARAM}"
                    logging.error(msg)
                    raise NameError,msg

                self.setParametersInTheStep(test_step) 
                self.__transform_command(test_step)
                ret = self.runner.run(test_step, self.parameters) #run the command
                
                #capture the return parameter
                if retvar != None and arges.util.introspection.isList(ret):
                    logging.info("saving return parameter. Key: " + str(retvar) + " Parameter: " + str(ret[1]))
                    #save the character as a valid regex pattern
                    self.parameters[arges.util.strings.formatTestParameter(retvar)] = str(ret[1])
                     
                #capture the return code of the function
                if arges.util.introspection.isList(ret):
                    ret = ret[0]
                
                logging.info("result: " + str(ret)) #print the result
                test_step.insert(0, ret) #insert the result into the step list
                number_of_results = number_of_results + 1 #increment the number of results 
    
                if not ret:
                    if isFatal:
                        logging.error("step failed and criticity is fatal. Stop running steps.")
                        break
                    else:
                        logging.warning("step failed but criticity is not fatal. Continue running steps.")
        finally:
            #close the windows if it is needed
            if closeWindows:
                logging.info("stopping browser if it is necessary")
                self.runner.run(["stopBrowser",None,None,None,None],self.parameters)
                    
        return number_of_results

    def __transform_command(self, test_step):
        """ This method transform certain commands that are not common. 
        For example the assignment operation has no command at all, so we map it to the
        setVar command"""
        
        for key in self.FUNCTION_TRANSFROMATION.keys():
            if test_step[self.COMMAND_COL] == key:
                test_step[self.COMMAND_COL] = self.FUNCTION_TRANSFROMATION[key]
                return

