# -*- coding: latin-1 -*-

""" random - returns a random string number, which is a number padded by fill_char  

parameters:
command = random_number_padding
target = length - the length of the number for example
fill_char = padding char

@author Adrián Deccico
"""

import logging
import random

#exposed command to the test api
def runCommand(length, fill_char, dummy):
    logging.debug("get random number with padding. Length: " 
                  + str(length) + " fill char: " + str(fill_char))
    random.seed()
    min = 0
    max = int(str("9").rjust(int(length),"9"))
    rand = random.randint(min, max)
    return [True, str(rand).rjust(int(length), fill_char)]
    

