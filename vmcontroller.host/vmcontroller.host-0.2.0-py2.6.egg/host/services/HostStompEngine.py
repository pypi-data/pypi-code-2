
try:
    import time
    import pdb
    import logging
    import inject
    import stomper

    from vmcontroller.common import BaseStompEngine 
    from vmcontroller.common import support, exceptions 
    from vmcontroller.common import destinations
except ImportError, e:
    print "Import error in %s : %s" % (__name__, e)
    import sys
    sys.exit()

#@inject.appscope
class HostStompEngine(BaseStompEngine):
  
  logger = logging.getLogger(support.discoverCaller())

  def __init__(self):
    super( HostStompEngine, self ).__init__()

  def connected(self, msg):
    #once connected, subscribe
    return ( stomper.subscribe(destinations.CONN_DESTINATION), 
             stomper.subscribe(destinations.CMD_RES_DESTINATION) )


