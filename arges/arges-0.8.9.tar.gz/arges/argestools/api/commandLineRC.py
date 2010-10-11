# -*- coding: latin-1 -*-

""" commandLineRC - command line that checks the return code

The purpose of this module is to provide a tool to test command line programs
by evaluating their return code  
@author Fernando Cuenca, Adrián Deccico
"""

import logging
import sys
import os

class CommandLineTestRC:
    def __init__(self):
        pass
    
    def runCommandAndLookSubString(self, args, retcode):
        logging.debug("executing: " + str(args))
        logging.debug("expecting return code: " + str(retcode))
        
        output = 0
        try:
            output = os.system(str(args))
        except:
            logging.warning("exception while running: " + str(args))
            logging.exception("exception info:")
        
        logging.debug("command returned: " + repr(output))
        return int(output) == int(retcode)            

cmd = CommandLineTestRC()    

#exposed command to the test api
def runCommand(args, retcode, dummy):
    """
    args = command line and its arguments
    retcode = expected return code 
    """
    return cmd.runCommandAndLookSubString(args, retcode)

