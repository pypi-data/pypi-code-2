# -*- coding: latin-1 -*-

""" readFile - read a file and return its content.

@return: [result, file content]

@author Adri�n Deccico
"""

import logging
import arges.util.files


#exposed command to the test api
def runCommand(file_name, dummy1, dummy2):
    logging.debug("creating: " + str(file_name))
    #@todo: try with a random name
    
    res = False
    text = ""
    if arges.util.files.isFile(file_name):
        try:
            with open(file_name) as f:
                text = f.read()
            res = True
        except:
            logging.exception("problem reading: " + str(file_name))
    
    return [res, text]
    
