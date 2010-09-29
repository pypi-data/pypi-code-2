# -*- coding: latin-1 -*-

""" commandLineTest - command line test api

The purpose of this module is to provide tools to test command line programs
by evaluating their output (return code or string output 
@author Adrián Deccico
"""

import logging
import re
import subprocess
import sys
import util.strings

class CommandLineTest:
    def __init__(self):
        pass
    
    def runCommandAndLookSubString(self, args, pattern):
        logging.debug("executing: " + str(args))
        logging.debug("looking for: " + str(pattern))
        
        output = ""
        res = True
        try:
            output = subprocess.Popen(args, stderr=subprocess.STDOUT, \
                                      stdout=subprocess.PIPE).communicate()[0]
        except:
            logging.warning("exception while running: " + str(args))
            logging.exception("exception info:")
            res = False
        
        logging.debug("command returned: " + repr(output))

        #look if the pattern is included in the output
        if res: 
            if (output == None or len(output)==0):
                output = ""
            if (pattern == None or len(pattern)==0):
                pattern = ""
            #if the pattern match, search will return an object
            res = re.search(unicode(pattern), output) != None
         
        return [res, output]
    

#------------------------------------------------------------------------------------------------
cmd = CommandLineTest()    

def processArgs(args):
    args = args.split(" ") #transform the string in a list
    args_processed = []
    for str in args:
        #cut the " but look if there any "" (a escaped ")
        args_processed.append(util.strings.replaceIfNotEscapedCharacter(str, '"', ""))
    return args_processed


#exposed command to the test api
def runCommand(args, substring, params):
    cmd_args = processArgs(args)
    additional_args = util.strings.formatTestParameter("${additional_arguments}")
    if params.has_key(additional_args):
        cmd_args.append(params[additional_args])
    return cmd.runCommandAndLookSubString(cmd_args, substring)
    

