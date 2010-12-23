# me2/exit.py
#
#

""" me2's finaliser """

## me2 imports

from me2.utils.trace import whichmodule
from plugins import plugs
from runner import defaultrunner, cmndrunner

## basic imports

import atexit
import os
import time
import sys
import logging

## functions

def globalshutdown():
    """ shutdown the bot. """
    defaultrunner.stop()
    cmndrunner.stop()
    sys.stdout.write("\n")
    logging.warn('shutting down'.upper())
    try:os.remove('me2.pid')
    except: pass
    from fleet import getfleet
    fleet = getfleet()
    if fleet:
        logging.info('shutting down fleet')
        fleet.exit()
    logging.info('shutting down plugins')
    plugs.exit()
    logging.info('done')
    #print "ltrs!"
    os._exit(0)

#try: import google
#except ImportError: atexit.register(globalshutdown)
