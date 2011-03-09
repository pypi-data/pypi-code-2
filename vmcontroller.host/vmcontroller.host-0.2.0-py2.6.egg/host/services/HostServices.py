"""
Represents the host, along with its supported operations. 
This module isn't meant to be used directly, but rather through the exposed
XMLRPC facade.
"""

try:
    import logging
    import inject
    import time
    import uuid
    import inspect

    from twisted.internet import defer, reactor
    from twisted.web import xmlrpc, server, resource

    from vmcontroller.common import support, exceptions
    from vmcontroller.common import EntityDescriptor
    from vmcontroller.host.controller import HyperVisorController
    from vmcontroller.host.services.FileTransferClient import FileTransferClient
except ImportError, e:
    print "Import error in %s : %s" % (__name__, e)
    import sys
    sys.exit()

@inject.appscope
class VMRegistry(object):
    """
    Keeps track of the registered virtual machines.
    """
    logger = logging.getLogger(support.discoverCaller())

    #PING/PONG
    #HELLO/BYE
    #STILL_ALIVE

    @inject.param('hvController')
    def __init__(self, hvController):
        self._vms = {}
        self._hvController = hvController
        self._idsToNames = self._getIdsToNamesMapping()
        self._namesToIds = dict( (v, k) for k,v in self._idsToNames.iteritems())

    def addVM(self, vmDescriptor):
        """
        @param vmDescriptor an instance of L{EntityDescriptor}
        """
        name = self.getNameForId( vmDescriptor.id )
        vmDescriptor.name = name
        self._vms[vmDescriptor.id] = vmDescriptor
        self.logger.info("VM '%s has joined the party" % self._vms[vmDescriptor.id].name )

    def removeVM(self, vmId): 
        """ Removes a VM from the party """
        vmDescriptor = self._vms.pop(vmId)
        self.logger.info("VM '%s' has left the party" % vmDescriptor.name )

    def isValid(self, vmId):
        return vmId in self._vms

    def __getitem__(self, vmId):
        return self._vms[vmId]

    def getRegisteredVMs(self):
        """ Returns a list of the registered VMs """
        return self._vms.keys()

    def getNameForId(self, vmId):
        name = self._idsToNames.get(vmId)
        if not name:
            self.logger.error("Unable to match VM ID '%s' to any registered VM (is \
                the VM controller really running from within a VM?)", str(vmId))
            raise exceptions.NoSuchVirtualMachine(str(vmId))
        else:
            return name

    def getIdForName(self, vmName):
        id_ = self._namesToIds.get(vmName)
        if not id_:
            self.logger.error("Unable to match VM name '%s' to any registered VM (is \
                the VM controller really running from within a VM?)", vmName)
            raise exceptions.NoSuchVirtualMachine(vmName)
        else:
            return id_ 

    def _getIdsToNamesMapping(self):
        def holder(): pass
        holder.res = None

        @defer.inlineCallbacks
        def _initializeIdsToNamesMapping():
            idsToNamesMap = yield self._hvController.getIdsToNamesMapping()
            self.logger.debug("Ids -> Names table initialized: %s" % idsToNamesMap)
            holder.res = idsToNamesMap
        
        _initializeIdsToNamesMapping()
        return holder.res

@inject.appscope
class CommandRegistry(object):
    """ 
    For all command-execution related. 

    Keeps track of requests made, served and retired
    """
    logger = logging.getLogger(support.discoverCaller())

    words = inject.attr('words')
    vmRegistry = inject.attr('vmRegistry', VMRegistry)

    def __init__(self):
        self._cmdReqsSent = {} #cmdId: dict with keys (timestamp, to, cmd, args, env, path)
        self._cmdReqsRetired = {} #finished cmdReqsSent
        self._cmdReqsRcvd = {}

    def addCmdRequest(self, cmdId, requestInfoDict):
        self._cmdReqsSent[cmdId] = requestInfoDict

    def processCmdResult(self, resultsMsg):
        serializedResults = resultsMsg['body'].split(None, 1)[1]
        #serializeded data: dict with keys (cmd-id, out, err, finished?, code/signal, resources)
        results = support.deserialize(serializedResults)
        self.logger.debug("Deserialized results: %s" % results)
        cmdId = results.pop('cmd-id')
        #this comes from a word.CMD_RESULT.listenAndAct
        #note down for which cmd we are getting the result back
        assert cmdId in self._cmdReqsSent
        self._cmdReqsRcvd[cmdId] = results
        self._cmdReqsRetired[cmdId] = self._cmdReqsSent.pop(cmdId)
        self.logger.info("Received command results for cmd-id '%s'", cmdId )

    def popCmdResults(self, cmdId):
        # for invalid cmdIds, returning None could
        # result in problems with xml-rpc. Thus we
        # resource to an empty string, which likewise
        # fails a boolean test
        return self._cmdReqsRcvd.pop(cmdId, "") 

    def listFinishedCmds(self):
        return self._cmdReqsRcvd.keys()

    def getCmdDetails(self, cmdId):
        details = self._cmdReqsSent.get(cmdId)
        if not details:
            details = self._cmdReqsRetired.get(cmdId)
        return support.serialize(details)

@inject.appscope
class FileTxs(object):
    """ 
    Handles the file transmission (to and from).
    """
    logger = logging.getLogger(support.discoverCaller())
    vmRegistry = inject.attr('VMRegistry', VMRegistry)
    
    def __init__(self):
        pass

    def cpFileToVM(self, vmId, pathToLocalFileName, pathToRemoteFileName = None ):
      """
      @param pathToRemoteFileName where to store the file, relative to the root of the server.
      If None, the basename of the source will be stored in the / of the server.
      """
      #this returns a deferred whose callbacks take care of returning the result
      if not self.vmRegistry.isValid(vmId):
          msg = "Invalid VM Id: '%s'" % vmId 
          self.logger.error(msg)
          dres = defer.fail(msg)
      else:
          if not pathToRemoteFileName:
              pathToRemoteFileName = pathToLocalFileName

          # FIXME get IP from the other interface "host-only-adapter"
          #vmIp = self.vmRegistry[vmId].ip 
          vmIp = "192.168.56.101"

          # TODO: Get these stuff automatically, from config...
          fileDirPath = '/home/rohit/temp'
          fileServerPort = 1234

          fileUtil = FileTransferClient(vmIp, fileServerPort, fileDirPath)
          # FIXME: Ugly hack to call putfile after 6 secs, assuming it will be connected by then
          dres = defer.Deferred()
          reactor.callLater(6, fileUtil.putFile, pathToLocalFileName, pathToRemoteFileName, dres)
          self.logger.debug("Transferring file: %s to VM(%s)" % (pathToLocalFileName, vmIp))

      return dres

    def cpFileFromVM(self, vmId, pathToRemoteFileName, pathToLocalFileName = None):
        #this returns a deferred whose callbacks take care of returning the result
        if not self.vmRegistry.isValid(vmId):
            msg = "Invalid VM Id: '%s'" % vmId 
            self.logger.error(msg)
            dres = defer.fail(msg)
        else:
            # FIXME get IP from the other interface "host-only-adapter"
            #vmIp = self.vmRegistry[vmId].ip 
            vmIp = "192.168.56.101"

            # TODO: Get these stuff automatically, from config...
            fileDirPath = '/home/rohit/temp'
            fileServerPort = 1234

            fileUtil = FileTransferClient(vmIp, fileServerPort, fileDirPath)
            # FIXME: Ugly hack to call putfile after 6 secs
            dres = defer.Deferred()
            reactor.callLater(1, fileUtil.getFile, pathToRemoteFileName, dres)
            self.logger.debug("Requesting file: %s from VM(%s)" % (pathToRemoteFileName, vmIp))
        return dres

def _fail(failure):
    HostXMLRPCService.logger.info("Exception on XMLRPC deferred:\n %s" % (failure.getBriefTraceback(),) )
    raise xmlrpc.Fault(-1, str(failure.value))

def _success(results):
    return results

class HostXMLRPCService(xmlrpc.XMLRPC, object):
    logger = logging.getLogger( support.discoverCaller() )
    vmRegistry = inject.attr('VMRegistry', VMRegistry)

    @inject.param('config')
    @inject.param('hvController')
    @inject.param('subject')
    def __init__(self, config, hvController, subject):
        xmlrpc.XMLRPC.__init__(self)
        self._config = config
        self._hvController = hvController
        self._createHVControllerMethods()
        self._host = subject

    #from xmlrpc.XMLRPC
    def _getFunction(self, functionPath):
        f = super(HostXMLRPCService, self)._getFunction(functionPath)
        # f is an xmlrpc_ method

        def wrapWithCallbacks(*args, **kw):
            return defer.maybeDeferred(f, *args, **kw).addCallbacks(_success, _fail)

        return wrapWithCallbacks 

    def makeEngineAccesible(self):
        siteRoot = resource.Resource()
        siteRoot.putChild('RPC2', self)
        port = int(self._config.get('xmlrpc', 'port'))
        listen_on = self._config.get('xmlrpc', 'host')
        try:
            reactor.listenTCP(port, server.Site(siteRoot), interface=listen_on) 
        except:
            self.logger.fatal("Unable to start XMLRPC interface, perhaps port in use. Exiting...")
            import sys
            sys.exit()

        self.logger.info("Listening on XMLRPC interface.")

    ###########################
    ## Operation on the VMs  ##
    ###########################

    def xmlrpc_ping(self, vm, timeout_secs=5.0): #FIXME: magic number of seconds
        """Pings a VM. vmcontroller.guest is required in the guest.
        @param vm: Virtual machine's name.
        @param timeout_secs: Timeout in seconds. Default is 5.0 secs."""
        vmId = self.vmRegistry.getIdForName(vm)
        return self._host.ping(vmId,timeout_secs)

    def xmlrpc_runCmd(self, toVmName, cmd, args=(), env={}, path=None, fileForStdin=''):
        cmdId = self._host.sendCmdRequest(toVmName, cmd, args, env, path, fileForStdin)
        return cmdId

    def xmlrpc_listFinishedCmds(self):
        return self._host.listFinishedCmds()

    def xmlrpc_getCmdResults(self, cmdId):
        return self._host.getCmdResults(cmdId)

    def xmlrpc_getCmdDetails(self, cmdId): 
        return self._host.getCmdDetails(cmdId)

    def xmlrpc_cpFileToVM(self, vmName, pathToLocalFileName, pathToRemoteFileName = None ):
        vmId = self.vmRegistry.getIdForName(vmName)
        return self._host.cpFileToVM(vmId, pathToLocalFileName, pathToRemoteFileName )

    def xmlrpc_cpFileFromVM(self, vmName, pathToRemoteFileName, pathToLocalFileName = None):
        vmId = self.vmRegistry.getIdForName(vmName)
        return self._host.cpFileFromVM(vmId, pathToRemoteFileName, pathToLocalFileName )

    ################################################
    ## Hypervisor controller dependent operations ##
    ################################################

    def _inspectHVControllerMethods(self):
        allMethods = inspect.getmembers(self._hvController, inspect.isfunction)
        publicMethods = filter( lambda method: method[0][0] != '_', allMethods )
        return publicMethods

    def _addMethod(self, method):
        name = 'xmlrpc_' + method.func_name
        setattr(self, name, method)

    def _createHVControllerMethods(self):
        self.hvControllerMethods = self._inspectHVControllerMethods()
        for method in self.hvControllerMethods:
            self._addMethod( method[1] )
            self.logger.debug("Controler method %s dynamically added" % method[0])

    def xmlrpc_help(self, methodName=None):
        if not methodName:
            allMethods = inspect.getmembers(self)
            xmlrpcMethods = filter( lambda method: method[0].startswith('xmlrpc_'), allMethods )
            methodNames = map( lambda m: m[0][len('xmlrpc_'):], xmlrpcMethods )
            resList = map( lambda mName: "%s" % self.xmlrpc_help(mName), methodNames )
            res = '\n\n'.join(resList)
        else:
            f = getattr(self, 'xmlrpc_' + methodName, None)
            if not f:
                raise ValueError('No such method: %s' % methodName)
            else:
                signature = _getPrintableFunctionSignature(f)
                res = '%s%s:\n%s' % (methodName, signature, f.__doc__ or '<No Docstring>',)

        return res

  
#########################################
## Helper functions
#########################################
def _getPrintableFunctionSignature(f):
    argSpec = inspect.getargspec(f)

    args = argSpec[0]
    if not args:
        args = ()
    else:
        if args[0] == 'self':
            del(args[0])

    defs = argSpec[3]
    if not defs:
        defs = ()

    argsWithDefs = reversed(map( lambda a,d: d and ( '%s=%s' % (a,d) ) or str(a), \
        reversed(args), reversed(defs) ) )

    return '(%s)' % (', '.join(argsWithDefs))


# TODO: Fix Host, add missing interfaces
@inject.appscope
class Host(object):
    logger = logging.getLogger( support.discoverCaller() )

    #we use injection so that we can do things lazily
    cmdRegistry = inject.attr('cmdRegistry', CommandRegistry)
    vmRegistry = inject.attr('vmRegistry', VMRegistry)
    fileTxs = inject.attr('fileTxs', FileTxs)

    words = inject.attr('words')
    stompProtocol = inject.attr('stompProtocol')

    def __init__(self):
        self._descriptor = EntityDescriptor('VMController-Host')
        self._vms = {}
        self._pings = {}

    @property
    def descriptor(self):
        return self._descriptor

    def ping(self, vmId, timeout_secs):
        def _timeout(timestamp):
            d = self._pings.pop(timestamp, None)
            if d:
                name = self.vmRegistry.getNameForId(vmId)
                d.errback(RuntimeError('PING timeout (for %s)' % name))

        timestamp = str(time.time())
        d = defer.Deferred()
        self._pings[timestamp] = d
        self.stompProtocol.sendMsg( self.words['PING']().howToSay( vmId ) )
        reactor.callLater(timeout_secs, _timeout, timestamp) 
        return d

    def processPong(self, msg):
        timestamp = msg['headers']['timestamp']
        d = self._pings.pop(timestamp, None)
        assert d
        vmId = msg['headers']['from']
        vmName = self.vmRegistry.getNameForId(vmId)
        d.callback('PONG from %s' % vmName)

    def sendCmdRequest(self, toVmName, cmd, args=(), env={}, path=None, fileForStdin=''):
        #get id for name
        toVmId = self.vmRegistry.getIdForName(toVmName)
        cmdId = str(uuid.uuid4())

        toSend = self.words['CMD_RUN']().  \
                 howToSay(toVmId, \
                     cmdId, cmd, args, \
                     env, path, fileForStdin )

        requestKeys = ('timestamp', 'toVmName', 'toVmId', 'cmd', 'args', 'env', 'path', 'fileForStdin')
        requestValues = (time.time(), toVmName, toVmId,  cmd, args, env, path, fileForStdin )

        self.stompProtocol.sendMsg( toSend )
        self.logger.info("Requested execution of command '%s' with cmd-id '%s'" % (cmd, cmdId))
        
        self.cmdRegistry.addCmdRequest(cmdId, dict( zip( requestKeys, requestValues) ))
        return cmdId

    def processCmdResult(self, resultsMsg):
        self.cmdRegistry.processCmdResult(resultsMsg)

    #XXX: make it possible to be blocking?
    def getCmdResults(self, cmdId):
        return self.cmdRegistry.popCmdResults(cmdId)

    ################################

    def addVM(self, vmDescriptor):
        self.vmRegistry.addVM(vmDescriptor)

    def removeVM():
        self.vmRegistry.removeVM(vmId)

    ################################

    def cpFileToVM(self, vmId, pathToLocalFileName, pathToRemoteFileName = None ):
        return self.fileTxs.cpFileToVM(vmId, pathToLocalFileName, pathToRemoteFileName)

    def cpFileFromVM(self, vmId, pathToRemoteFileName, pathToLocalFileName = None):
        return self.fileTxs.cpFileFromVM(vmId, pathToRemoteFileName, pathToLocalFileName)
