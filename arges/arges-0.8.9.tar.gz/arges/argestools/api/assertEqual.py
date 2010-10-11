# -*- coding: latin-1 -*-

""" assertEqual - test the equality of a string against another

@author Adrián Deccico
"""

import logging


#exposed command to the test api
def runCommand(original_string, challenge_string, dummy):
    logging.debug("comparing: " + str(original_string) + " with: " + str(challenge_string))
    return original_string == challenge_string
    

