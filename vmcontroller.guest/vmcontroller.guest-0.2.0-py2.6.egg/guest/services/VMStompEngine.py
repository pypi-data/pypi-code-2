
try:
    import stomper
    import logging
    import netifaces
    import inject
    
    from twisted.internet.task import LoopingCall
    
    from vmcontroller.common import EntityDescriptor
    from vmcontroller.common import BaseStompEngine 
    from vmcontroller.common import support, exceptions 
    from vmcontroller.common import destinations
except ImportError, e:
    print "Import error in %s : %s" % (__name__, e)
    import sys
    sys.exit()

class VMStompEngine(BaseStompEngine):
  """ This basically models a client (ie, VM instance)"""
  
  logger = logging.getLogger(support.discoverCaller())

  config = inject.attr("config")
  words = inject.attr("words")
  stompProtocol = inject.attr('stompProtocol', scope=inject.appscope)


  def __init__(self):
    super( VMStompEngine, self).__init__()
 
    networkInterface = self.config.get('guest', 'network_interface')

    networkInterfaceData = netifaces.ifaddresses(networkInterface)
    #FIXME Get IPs of all interfaces, especially the host-only adapter...
    self._id, self._ip = [ networkInterfaceData[af][0]['addr'] for af in (netifaces.AF_LINK, netifaces.AF_INET) ]
    self._id = self._id.upper()
    self.logger.debug("VM instantiated with id/ip %s/%s" % (self._id, self._ip) )

    self._descriptor = EntityDescriptor(self._id, ip=self._ip)


  @property
  def descriptor(self):
    return self._descriptor

  def connected(self, msg):
    res = []
    #once connected, subscribe
    res.append(stomper.subscribe(destinations.CMD_REQ_DESTINATION))

    #announce ourselves
    res.append( self.words['HELLO']().howToSay() )
 
    return tuple(res)

  def pong(self, pingMsg):
    self.logger.debug("Sending reply to received ping: ", pingMsg )
    self.stompProtocol.sendMsg( self.words['PONG']().howToSay(pingMsg) )

  def dealWithExecutionResults(self, results):
    resultsFields = ('cmd-id', 'out', 'err', 'finished', 'exitCodeOrSignal', 'resources' )
    #see CommandExecuter.getExecutionResults

    resultsDict = dict( zip( resultsFields, results ) )
    #self.protocol got injected by StompProtocol
    self.stompProtocol.sendMsg( self.words['CMD_RESULT']().howToSay(resultsDict) )

  @property
  def id(self):
    return self._id

  @property
  def ip(self):
    return self._ip

  def __repr__(self):
    return "VM with ID/IP: %s/%s" % (self.id, self.ip)

  
