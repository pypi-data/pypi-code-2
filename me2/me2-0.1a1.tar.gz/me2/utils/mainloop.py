# me2/utils/mainloop.py
#
#

""" main loop used in me2 binairies. """

## me2 imports

from me2.lib.eventhandler import mainhandler
from me2.lib.exit import globalshutdown

## basic imports

import os
import time

## mainloop function

def mainloop():
    """ function to be used as mainloop. """
    while 1:
        try:
            time.sleep(1)
            mainhandler.handle_one()
        except KeyboardInterrupt: break
        except Exception, ex:
            handle_exception()
            globalshutdown()
            os._exit(1)
    globalshutdown()
    os._exit(0)
