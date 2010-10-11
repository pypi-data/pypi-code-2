# -*- coding: latin-1 -*-

""" pexpectWrapper - run Pexpect commands

This is a wrapper of the Pexpect library.

Pexpect is a Python module for spawning child applications and controlling
them automatically. Pexpect does not use C, Expect, or TCL extensions. 
Pexpect should work on any platform that supports the standard Python pty module. 
 
@author Adrián Deccico, migrated from old AT tools
"""
import logging

import arges.util.introspection
import thirdparty.pexpect 

class PexpectWrapper:
    
    def __init__(self):
        self.pexpect = 0  #init in null in order to detect its type
        self.runners = {} #dictionary of available runners key=name, value=object_runner
        self.runners["self"] = self  #just this object will be the runner
        self.curExpectChild = None
        self.params = {}

    def hasProxiedCommand(self, command):
        #check if the command is within this class
        logging.debug("check if: " + str(command) + " is registered in the PexpectWrapper")
        
        try:
            for x in self.runners.values():
                f = getattr(x, command, 0)
                if  f != 0 and callable(f):
                    logging.info(str(command) + \
                                  " is registered in the PexpectWrapper")
                    return True
        except:
            #try to find the function in the registered objects, 
            #but no matter if we have no luck
            pass  
        
        logging.debug(str(command) + " is not registered in the PexpectWrapper")
        return False
    
    def runProxiedCommand(self, cmd, target, value, additional_parameters):
        #run a command against the PexpectWrapper.
        #precondition: the hasProxiedCommand command has to be true for this command
        
        self.params = additional_parameters
        
        #check if the command is within Pexpect api or the helper class
        logging.debug("running: " + str(cmd) + " " + str(target) + " " + str(value))
        try:
            for x in self.runners.values():
                f = getattr(x, cmd, 0)
                if  f != 0 and callable(f):
                    #results of the commands
                    ret = False

                    #run the command with the correct number of parameters
                    #this is due to the lack of overloading in Python
                    logging.debug("executing command: " + str(cmd))
                    if target == None and value == None:
                        ret = f()
                    else:
                        if target != None and value == None:
                            ret = f(target)
                        else:
                            ret = f(target, value)
                    
                    if ret == None: 
                        ret = True 
                    elif ret == False:
                        ret = False
                    else:
                        #if the function returns something, then a list with a True and the result is returned
                        ret = [True, ret]

                    return ret
        except:
            #try to find the function in the registered objects, 
            #but no matter if we have no luck
            logging.warning("problems running " + str(cmd) + " in the PexpectWrapper module. ")
            logging.exception("exception info:")
            return False
        
    def pexec(self, cmd):
        """
          NAME: pexec
          SYNOPSIS: launch a 'cmd' using pexpect.spawn()
          RETURN VALUE: [result, pid]
        """
        pid = 0
        try:
            logging.debug("initializing pexpect")
            self.curExpectChild = thirdparty.pexpect.spawn(cmd)
            logging.info(" spawned PID="+str(self.curExpectChild.__dict__['pid']))
            pid = str(self.curExpectChild.__dict__['pid'])
        except:
            self.curExpectChild.kill(0)
            logging.warning("problems running pexec: " + str(cmd))
            logging.exception("exception info:")
            return False
        
        return [arges.util.introspection.isInstance(self.curExpectChild), pid]

    def expect(self, pattern, timeout=120):
        """
          SYNOPSIS: expect 'str' from stdout/stderr of the curExpectChild launched by pexec
                     waits 'timeout' seconds
          EXCEPTIONS: when curExpectChild.expect() reachs exceptions, timeout or EOF
          XXX : ver exceptions, cuando encuentra un VDDSException en alguna aplicacion
        """

        try:
            logging.debug("calling expect, pattern: " + str(pattern))
            astr=eval('"' + pattern + '"') #A: str with all escape chars processed
            logging.debug("expecting '" + astr + "'")
            timeout = int(timeout)
            logging.debug("Timeout: " + str(timeout)) 
            index = self.curExpectChild.expect(astr, timeout)
            logging.info("stdout " + "{{{" + self.curExpectChild.before + "}}}")
            if index == 1:
                logging.error(" failed. Pattern 'NOT FOUND'")
                raise
            elif index == 2:
                logging.error(" failed. 'TIMEOUT'")
                raise
            elif index == 3:
                logging.error(" failed. 'REACH EOF'")
                raise
            output = str(self.getPexpectValue()[1])
            logging.debug("output:" + output)
            return [True, output]
        except:
            self.curExpectChild.kill(0)
            logging.warning("problems running expect: " + str(pattern) + " in the pexpectWrapper module. ")
            logging.exception("exception info:")
            return False

    def expectEof(self, timeout=120):
        try:
            logging.debug("calling expectEof")
            index = curExpectChild.expect(pexpect.EOF, timeout=int(timeout))
            logging.info("ACTION print stdout " + "{{{" + self.curExpectChild.before + "}}}")
            if index == 1:
                logging.error(" Fail. Pattern 'NOT FOUND'")
                raise
            elif index == 2:
                logging.error(" Fail. 'TIMEOUT'")
                raise
            elif index == 3:
                logging.error(" Fail. 'REACH EOF'")
                raise
            return True
        except:
            self.curExpectChild.kill(0)
            logging.warning("problems running expectEof")
            logging.error(" print stdout: " + "{{{" + self.curExpectChild.before + "}}}")
            logging.exception("exception info:")
            return False

    def send(self, string_value=""):
        """
          NAME: send
          SYNOPSIS: sendline 'str' to stdin of the curExpectChild launched by pexec
        """
        try:
            logging.debug("ACTION send " + str(string_value))
            if string_value==None: string_value=""
            astr=eval('"' + string_value + '"') #A: str with all escape chars processed
            logging.debug("ACTION "+ "sending astr = '" + astr + "'" )
            self.curExpectChild.sendline(astr)
            return [True, self.getPexpectValue()[1]]
        except:
            self.curExpectChild.kill(0)
            logging.error("ACTION send failed with string: " +str(string_value))
            logging.exception("exception info:")
            return False
    
    def getPexpectValue(self):
        """get last pexpect value"""
        logging.debug("calling getPexpectValue")
        ret_text = ""
        try:
            ret_text = str(self.curExpectChild.before)
            logging.debug("returning: " + ret_text)
        except:
            self.killProcess() #@todo execute this at the end, like stopBrowser
            pass
        return [True, ret_text]

    def killProcess(self):
        """kill the created child process"""
        logging.debug("killing the pexec process")
        try:
            self.curExpectChild.kill(0)
        except:
            pass
        
#-------------------------------------------------------------------------------         
    
pex = PexpectWrapper() #Pexpect wrapper object
   
def runProxiedCommand(cmd, target, value, params):
    #exposed command to the test api
    return pex.runProxiedCommand(cmd, target, value, params)

def hasProxiedCommand(cmd):
    #exposed command to the test api
    return pex.hasProxiedCommand(cmd)
