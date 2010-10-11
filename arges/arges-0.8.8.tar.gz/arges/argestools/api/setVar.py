# -*- coding: latin-1 -*-

""" setVar - set a variable

@author Adrián Deccico
"""

import logging


#exposed command to the test api
def runCommand(value, dummy, dummy2):
    """
    expected format:
    setVar,new_var,,${PARAMETER_TO_BE_CHANGED},fatal

    pos: change ${PARAMETER_TO_BE_CHANGED} with 'new_var'
    """
    if value == None or len(str(value)) < 1:
        value = ""
    logging.debug("value: " + str(value))
    return [True, value]
    

