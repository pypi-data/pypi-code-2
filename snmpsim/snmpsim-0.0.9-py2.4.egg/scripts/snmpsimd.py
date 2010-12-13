#
# SNMP Devices Simulator
#
# Written by Ilya Etingof <ilya@glas.net>, 05/2010
#
import os
import sys
import string
import getopt
import hashlib
import time
import anydbm
import whichdb
import bisect
from pyasn1.type import univ
from pyasn1.codec.ber import encoder, decoder
from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import cmdrsp, context
from pysnmp.carrier.asynsock.dgram import udp
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.smi import exval, indices
from pysnmp.proto import rfc1902, api
from pysnmp import debug

# Process command-line options

# Defaults
forceIndexBuild = False
validateData = False
v2cArch = False
v3User = 'simulator'
v3AuthKey = 'auctoritas'
v3PrivKey = 'privatus'
v3PrivProto = config.usmDESPrivProtocol
agentAddress = ('127.0.0.1', 161)
deviceDir = '.'
deviceExt = os.path.extsep + 'snmpwalk'

helpMessage = 'Usage: %s [--help] [--debug=<category>] [--device-dir=<dir>] [--force-index-rebuild] [--validate-device-data] [--agent-address=<X.X.X.X>] [--agent-port=<port>] [--v2c-arch ] [--v3-user=<username>] [--v3-auth-key=<key>] [--v3-priv-key=<key>] [--v3-priv-proto=<DES|AES>]' % sys.argv[0]

try:
    opts, params = getopt.getopt(sys.argv[1:], 'h',
        ['help', 'debug=', 'device-dir=', 'force-index-rebuild', 'validate-device-data', 'agent-address=', 'agent-port=', 'v2c-arch', 'v3-user=', 'v3-auth-key=', 'v3-priv-key=', 'v3-priv-proto=']
        )
except Exception, why:
    print why
    print helpMessage
    sys.exit(-1)

if params:
    print 'extra arguments supplied %s\n' % (params) + helpMessage
    sys.exit(-1)

for opt in opts:
    if opt[0] == '-h' or opt[0] == '--help':
        print helpMessage
        sys.exit(-1)
    if opt[0] == '--debug':
        debug.setLogger(debug.Debug(opt[1]))
    if opt[0] == '--device-dir':
        deviceDir = opt[1]
    if opt[0] == '--force-index-rebuild':
        forceIndexBuild = True
    if opt[0] == '--validate-device-data':
        validateData = True
    if opt[0] == '--agent-address':
        agentAddress = (opt[1], agentAddress[1])
    if opt[0] == '--agent-port':
        agentAddress = (agentAddress[0], string.atoi(opt[1]))
    if opt[0] == '--v2c-arch':
        v2cArch = True
    if opt[0] == '--v3-user':
        v3User = opt[1]
    if opt[0] == '--v3-auth-key':
        v3AuthKey = opt[1]
    if opt[0] == '--v3-priv-key':
        v3PrivKey = opt[1]
    if opt[0] == '--v3-priv-proto':
        if opt[1].upper() == 'DES':
            v3PrivProto = config.usmDESPrivProtocol
        elif opt[1].upper() == 'AES':
            v3PrivProto = config.usmAesCfb128Protocol
        else:
            print 'bad v3 privacy protocol'
            sys.exit(-1)

# Device file entry parsers

class DumpParser:
    ext = os.path.extsep + 'dump'
    tagMap = {
        '0': rfc1902.Counter32,
        '1': rfc1902.Gauge32,
        '2': rfc1902.Integer32,
        '3': rfc1902.IpAddress,
        '4': univ.Null,
        '5': univ.ObjectIdentifier,
        '6': rfc1902.OctetString,
        '7': rfc1902.TimeTicks,
        '8': rfc1902.Counter32,  # an alias
        '9': rfc1902.Counter64,
        }

    def __nullFilter(value):
        return "" # simply drop whatever value is there when it's a Null
    
    def __unhexFilter(value):
        if value[:5].lower() == "hex: ":
            value = ''.join(map(chr, map(lambda x: string.atoi(x, 16),
                                     value[5:].split('.'))))
        elif value[0] == '"' and value[-1] == '"':
            value = value[1:-1]
        return value

    filterMap = {
        '4': __nullFilter,
        '6': __unhexFilter
        }

    def parse(self, line): return line.split('|', 2)

    def evaluateOid(self, oid):
        return univ.ObjectIdentifier(oid)

    def evaluateValue(self, tag, value):
        return tag, self.tagMap[tag](
            self.filterMap.get(tag, lambda x: x)(value.strip())
            )
    
    def evaluate(self, line, oidOnly=False, muteValueError=True):
        oid, tag, value = self.parse(line)
        if oidOnly:
            value = None
        else:
            try:
                tag, value = self.evaluateValue(tag, value)
            except:
                if muteValueError:
                    value = rfc1902.OctetString(
                        'SIMULATOR VALUE ERROR %s' % repr(value)
                        )
                else:
                    raise
        return self.evaluateOid(oid), value

class MvcParser(DumpParser):
    ext = os.path.extsep + 'MVC'  # just an alias

class SnmprecParser:
    ext = os.path.extsep + 'snmprec'
    tagMap = {}
    for t in ( rfc1902.Gauge32,
               rfc1902.Integer32,
               rfc1902.IpAddress,
               univ.Null,
               univ.ObjectIdentifier,
               rfc1902.OctetString,
               rfc1902.TimeTicks,
               rfc1902.Opaque,
               rfc1902.Counter32,
               rfc1902.Counter64 ):
        tagMap[str(reduce(lambda x,y: x+y, t.tagSet[0]))] = t

    def parse(self, line): return line.strip().split('|', 2)

    def evaluateOid(self, oid):
        return univ.ObjectIdentifier(oid)
    
    def evaluateValue(self, tag, value):
        # Unhexify
        if tag[-1] == 'x':
            tag = tag[:-1]
            value = ''.join(
                map(lambda x: chr(int(value[x:x+2], 16)),
                    range(0, len(value), 2))
                )
        return tag, self.tagMap[tag](value)

    def evaluate(self, line, oidOnly=False, muteValueError=True):
        oid, tag, value = self.parse(line)
        if oidOnly:
            value = None
        else:
            try:
                tag, value = self.evaluateValue(tag, value)                
            except:
                if muteValueError:
                    value = rfc1902.OctetString(
                        'SIMULATOR VALUE ERROR %s' % repr(value)
                        )
                else:
                    raise
        return self.evaluateOid(oid), value

parserSet = {
    DumpParser.ext: DumpParser(),
    MvcParser.ext: MvcParser(),
    SnmprecParser.ext: SnmprecParser()
    }

# Device text file and OID index

class DeviceFile:
    openedQueue = []
    maxQueueEntries = 31  # max number of open text and index files
    def __init__(self, textFile):
        self.__textFile = textFile
        try:
            self.__dbFile = textFile[:textFile.rindex(os.path.extsep)]
        except ValueError:
            self.__dbFile = textFile
        finally:
            self.__dbFile = self.__dbFile + os.path.extsep + 'dbm'
    
        self.__db = self.__text = None
        self.__dbType = '?'
        
    def indexText(self, textParser, forceIndexBuild=False):
        textFileStamp = os.stat(self.__textFile)[8]

        # gdbm on OS X seems to voluntarily append .db, trying to catch that
        
        indexNeeded = forceIndexBuild
        
        for dbFile in (
            self.__dbFile + os.path.extsep + 'db',
            self.__dbFile
            ):
            if os.path.exists(dbFile):
                if textFileStamp < os.stat(dbFile)[8]:
                    if indexNeeded:
                        print "Forced index rebuild %s" % dbFile
                else:
                    indexNeeded = True
                    print "Index %s out of date" % dbFile
                break
        else:
            indexNeeded = True
            print "Index does not exist for %s" % self.__textFile
            
        if indexNeeded:
            print "Indexing device file %s..." % self.__textFile

            text = open(self.__textFile)
            
            db = anydbm.open(self.__dbFile, 'n')
        
            lineNo = 0
            offset = 0
            while 1:
                line = text.readline()
                if not line:
                    break
            
                lineNo = lineNo + 1

                try:
                    oid, tag, val = textParser.parse(line)
                except Exception, why:
                    db.close()
                    os.remove(self.__dbFile)
                    raise Exception(
                        'Data error at %s:%d: %s' % (
                            self.__textFile, lineNo, why
                            )
                        )

                if validateData:
                    try:
                        textParser.evaluateOid(oid)
                    except Exception, why:
                        db.close()
                        os.remove(self.__dbFile)
                        raise Exception(
                            'OID error at %s:%d: %s' % (
                                self.__textFile, lineNo, why
                                )
                            )
                    try:
                        textParser.evaluateValue(tag, val)
                    except Exception, why:
                        print '*** Error at line %s, value %s: %s' % (
                            lineNo, repr(val), why
                            )
                        
                db[oid] = str(offset)

                offset = text.tell()

            text.close()
            db.close()
        
            print "...%d entries indexed" % (lineNo - 1,)

        self.__dbType = whichdb.whichdb(self.__dbFile)

        return self

    def close(self):
        self.__text.close()
        self.__db.close()
        self.__db = self.__text = None
    
    def getHandles(self):
        if self.__db is None:
            if len(DeviceFile.openedQueue) > self.maxQueueEntries:
                DeviceFile.openedQueue[0].close()
                del DeviceFile.openedQueue[0]

            DeviceFile.openedQueue.append(self)

            self.__text = open(self.__textFile)

            self.__db = anydbm.open(self.__dbFile)

        return self.__text, self.__db

    def __str__(self):
        return 'file %s, %s-indexed, %s' % (
            self.__textFile, self.__dbType, self.__db and "opened" or "closed"
            )

# Collect device files

def getDevices(topDir, dirDepth=None):
    if dirDepth is None:
        dirDepth = len(topDir.split(os.path.sep))
    files = os.listdir(topDir)
    dirContent = []
    for dFile in files:
        path = topDir + os.path.sep + dFile
        inode = os.stat(path)
        if inode[0] & 0x4000:
            dirContent = dirContent + getDevices(path, dirDepth)
            continue            
        if not (inode[0] & 0x8000):
            continue
        try:
            dExt = dFile[dFile.rindex(os.path.extsep):]
        except ValueError:
            continue
        if not parserSet.has_key(dExt):
            continue
        fullPath = topDir + os.path.sep + dFile
        contextName = fullPath.split(os.path.sep)[dirDepth:]
        dirContent.append(
            (fullPath,
             parserSet[dExt],
             os.path.sep.join(contextName)[:-len(dExt)])
            )
    return dirContent

# Lightweignt MIB instrumentation (API-compatible with pysnmp's)

class MibInstrumController:
    def __init__(self, deviceFile, textParser):
        self.__deviceFile = deviceFile
        self.__textParser = textParser

    def __str__(self): return str(self.__deviceFile)

    # In-place, by-OID binary search

    def __searchOid(self, text, oid):
        lo = mid = 0
        text.seek(0, 2)
        hi = sz = text.tell()
        while lo < hi:
            mid = (lo+hi)//2
            while mid:
                text.seek(mid)
                c = text.read(1)
                if c == '\n':
                    mid = mid + 1
                    break
                mid = mid - 1
            if not mid:
                text.seek(mid)
            line = text.readline()
            try:
                midval, _ = self.__textParser.evaluate(line, oidOnly=True)
            except Exception, why:
                raise Exception(
                    'Data error at %s for %s: %s' % (self, oid, why)
                    )                
            if midval < oid:
                lo = mid + len(line)
            elif midval > oid:
                hi = mid
            else:
                return mid
            if mid >= sz:
                return sz
        if lo == mid:
            return lo
        else:
            return hi

    def __doVars(self, varBinds, nextFlag=False, writeMode=False):
        rspVarBinds = []

        if nextFlag:
            errorStatus = exval.endOfMib
        else:
            errorStatus = exval.noSuchInstance

        text, db = self.__deviceFile.getHandles()
        
        for oid, val in varBinds:
            textOid = reduce(lambda x,y: '%s.%s' % (x, y), oid)
            if db.has_key(textOid):
                offset = db[textOid]
                exactMatch = True
            else:
                if nextFlag:
                    offset = self.__searchOid(text, oid)
                    exactMatch = False
                else:
                    rspVarBinds.append((oid, errorStatus))
                    continue

            offset = long(offset)

            text.seek(offset)

            line = text.readline()

            if nextFlag and exactMatch:
                line = text.readline()

            if not line:
                rspVarBinds.append((oid, errorStatus))
                continue

            try:
                oid, val = self.__textParser.evaluate(line)
            except Exception, why:
                raise Exception(
                    'Data error at %s for %s: %s' % (self, textOid, why)
                    )

            rspVarBinds.append((oid, val))

        return rspVarBinds
    
    def readVars(self, varBinds, (acFun, acCtx)=(None, None)):
        return self.__doVars(varBinds, False)

    def readNextVars(self, varBinds, (acFun, acCtx)=(None, None)):
        return self.__doVars(varBinds, True)

    def writeVars(self, varBinds, (acFun, acCtx)=(None, None)):
        return self.__doVars(varBinds, False, True)

# Devices index as a MIB instrumentaion at a dedicated SNMP context

class DevicesIndexInstrumController:
    def __init__(self, baseOid=(1, 3, 6, 1, 4, 1, 20408, 999, 1)):
        self.__db = indices.OidOrderedDict()
        self.__baseOid = baseOid
        self.__idx = 1

    def readVars(self, varBinds, (acFun, acCtx)=(None, None)):
        return map(
            lambda (o,v): (o, self.__db.get(o, exval.noSuchInstance)),
            varBinds
            )

    def __getNextVal(self, key, default):
        try:
            key = self.__db.nextKey(key)
        except KeyError:
            return key, default
        else:
            return key, self.__db[key]
                                                            
    def readNextVars(self, varBinds, (acFun, acCtx)=(None, None)):
        return map(
            lambda (o,v): self.__getNextVal(o, exval.endOfMib), varBinds
            )
    
    def writeVars(self, varBinds, (acFun, acCtx)=(None, None)):
        return map(
            lambda (o,v): (o, exval.noSuchInstance), varBinds
            )

    def addDevice(self, *args):
        for idx in range(len(args)):
            self.__db[
                self.__baseOid + (idx+1, self.__idx)
                ] = rfc1902.OctetString(args[idx])
        self.__idx = self.__idx + 1

devicesIndexInstrumController = DevicesIndexInstrumController()

# Basic SNMP engine configuration

if v2cArch:
    contexts = {}
else:
    snmpEngine = engine.SnmpEngine()

    config.addContext(snmpEngine, '')

    snmpContext = context.SnmpContext(snmpEngine)
        
    config.addV3User(
        snmpEngine, v3User,
        config.usmHMACMD5AuthProtocol, v3AuthKey,
        v3PrivProto, v3PrivKey
        )

# Build pysnmp Managed Objects base from device files information

for fullPath, textParser, communityName in getDevices(deviceDir):
    mibInstrum = MibInstrumController(
        DeviceFile(fullPath).indexText(textParser, forceIndexBuild), textParser
        )

    print """Device %s
SNMPv1/2c community name: %s""" % (mibInstrum, communityName)
    
    if v2cArch:
        contexts[communityName] = mibInstrum

        devicesIndexInstrumController.addDevice(
            fullPath, communityName
            )
    else:
        agentName = contextName = hashlib.md5(communityName).hexdigest()
        
        config.addV1System(snmpEngine, agentName,
                           communityName, contextName=contextName)

        snmpContext.registerContextName(
            contextName, mibInstrum
            )

        devicesIndexInstrumController.addDevice(
            fullPath, communityName, contextName
            )

        print """SNMPv3 context name: %s
""" % (contextName,)

if v2cArch:
    def getBulkHandler(varBinds, nonRepeaters, maxRepetitions, readNextVars):
        if nonRepeaters < 0: nonRepeaters = 0
        if maxRepetitions < 0: maxRepetitions = 0
        N = min(nonRepeaters, len(varBinds))
        M = int(maxRepetitions)
        R = max(len(varBinds)-N, 0)
        if nonRepeaters:
            rspVarBinds = readNextVars(varBinds[:int(nonRepeaters)])
        else:
            rspVarBinds = []
        if M and R:
            for i in range(N,  R):
                varBind = varBinds[i]
                for r in range(1, M):
                    rspVarBinds.extend(readNextVars((varBind,)))
                    varBind = rspVarBinds[-1]

        return rspVarBinds
    
    def commandResponderCbFun(transportDispatcher, transportDomain,
                              transportAddress, wholeMsg):
        while wholeMsg:
            msgVer = api.decodeMessageVersion(wholeMsg)
            if api.protoModules.has_key(msgVer):
                pMod = api.protoModules[msgVer]
            else:
                print "Unsupported SNMP version %s" % msgVer
                return
            reqMsg, wholeMsg = decoder.decode(
                wholeMsg, asn1Spec=pMod.Message(),
                )
            
            communityName = reqMsg.getComponentByPosition(1)
            if not contexts.has_key(communityName):
                print "Unknown community name %s from %s:%s\n" % (
                    communityName, transportDomain, transportAddress
                    )
                return wholeMsg
            
            rspMsg = pMod.apiMessage.getResponse(reqMsg)
            rspPDU = pMod.apiMessage.getPDU(rspMsg)        
            reqPDU = pMod.apiMessage.getPDU(reqMsg)
    
            if reqPDU.isSameTypeWith(pMod.GetRequestPDU()):
                backendFun = contexts[communityName].readVars
            elif reqPDU.isSameTypeWith(pMod.SetRequestPDU()):
                backendFun = contexts[communityName].writeVars
            elif reqPDU.isSameTypeWith(pMod.GetNextRequestPDU()):
                backendFun = contexts[communityName].readNextVars
            elif hasattr(pMod, 'GetBulkRequestPDU') and \
                     reqPDU.isSameTypeWith(pMod.GetBulkRequestPDU()):
                if not msgVer:
                    print "GETBULK over SNMPv1 from %s:%s\n" % (
                        transportDomain, transportAddress
                        )
                    return wholeMsg
                backendFun = lambda varBinds: getBulkHandler(varBinds,
                    pMod.apiBulkPDU.getNonRepeaters(reqPDU),
                    pMod.apiBulkPDU.getMaxRepetitions(reqPDU),
                    contexts[communityName].readNextVars)
            else:
                print "Unsuppored PDU type %s from %s:%s\n" % (
                    reqPDU.__class__.__name__, transportDomain,
                    transportAddress
                    )
                return wholeMsg
    
            varBinds = backendFun(
                pMod.apiPDU.getVarBinds(reqPDU)
                )

            # Poor man's v2c->v1 translation
            
            if not msgVer:
                for idx in range(len(varBinds)):
                    oid, val = varBinds[idx]
                    if val.tagSet in (rfc1902.Counter64.tagSet,
                                      univ.Null.tagSet):
                        varBinds = pMod.apiPDU.getVarBinds(reqPDU)
                        pMod.apiPDU.setErrorStatus(rspPDU, 5)
                        pMod.apiPDU.setErrorIndex(rspPDU, idx+1)
                        break

            pMod.apiPDU.setVarBinds(rspPDU, varBinds)
            
            transportDispatcher.sendMessage(
                encoder.encode(rspMsg), transportDomain, transportAddress
                )
            
        return wholeMsg

    # Configure access to devices index
    
    contexts['index'] = devicesIndexInstrumController
    
    # Configure socket server
    
    transportDispatcher = AsynsockDispatcher()
    transportDispatcher.registerTransport(
            udp.domainName, udp.UdpTransport().openServerMode(agentAddress)
            )
    transportDispatcher.registerRecvCbFun(commandResponderCbFun)
else:
    print """SNMPv3 credentials:
Username: %s
Authentication key: %s
Encryption (privacy) key: %s
Encryption protocol: %s""" % (v3User, v3AuthKey, v3PrivKey, v3PrivProto)

    # Configure access to devices index

    config.addV1System(snmpEngine, 'index',
                       'index', contextName='index')

    snmpContext.registerContextName(
        'index', devicesIndexInstrumController
        )

    # Configure socket server

    config.addSocketTransport(
        snmpEngine,
        udp.domainName,
        udp.UdpTransport().openServerMode(agentAddress)
        )

    # SNMP applications

    cmdrsp.GetCommandResponder(snmpEngine, snmpContext)
    cmdrsp.SetCommandResponder(snmpEngine, snmpContext)
    cmdrsp.NextCommandResponder(snmpEngine, snmpContext)
    cmdrsp.BulkCommandResponder(snmpEngine, snmpContext)

    transportDispatcher = snmpEngine.transportDispatcher
    
print """
Listening at %s
""" % (agentAddress,)

# Run mainloop

transportDispatcher.jobStarted(1) # server job would never finish
transportDispatcher.runDispatcher()
