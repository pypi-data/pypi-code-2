# -*- coding: latin-1 -*-

""" random - give a random integer number

parameters:
command = random
target = a
value = b
Return a random integer N such that a <= N <= b.

@author Adrián Deccico
"""

import logging
import random as rand

#exposed command to the test api
def runCommand(a, b, dummy):
    logging.debug("returning random integer bigger than: " + a + " and smaller than: " + b)
    rand.seed()
    return [True, rand.randint(int(a), int(b))]