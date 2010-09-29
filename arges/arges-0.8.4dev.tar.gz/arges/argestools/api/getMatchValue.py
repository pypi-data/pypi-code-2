# -*- coding: latin-1 -*-

""" getMatchValue - save first captured group from "pattern"  

@author Adrián Deccico, based on Javier Fuchs and Mauricio Cappella old AT 
"""

import logging
import re


#exposed command to the test api
def runCommand(pattern, text, dummy2):
    try:
        logging.debug("getMatchValue called. Pattern: " + str(pattern) + " text: " + str(text))
        if pattern == None: pattern = ""
        if text == None: text = ""
        match= re.search(pattern, text)
        value = match and match.group(1) or ""
        logging.debug(" value '" +str(value)+ "' obtained with pattern='" 
                      +str(re)+ " from text: " + str(text))
        return [value != None, value] 
    except:
        logging.exception("getMatchValue failed. Pattern: " + str(pattern) + " text: " + str(text))
        return [False, ""]
