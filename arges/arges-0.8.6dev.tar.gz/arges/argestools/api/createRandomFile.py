# -*- coding: latin-1 -*-

""" createRandomFile - create a file based on the file_name name.
Trying with different (incremental) names.

@return: [result, file name]

@author Adrián Deccico
"""

import logging


#exposed command to the test api
def runCommand(file_name, text_content, dummy2):
    logging.debug("creating: " + str(file_name))
    #@todo: try with a random name
    
    res = True
    try:
        with open(file_name, 'w') as f:
            f.write(text_content)
    except:
        logging.exception("problem creating and writing: " + str(file_name))
        res = False
    
    return [res, file_name]
    
