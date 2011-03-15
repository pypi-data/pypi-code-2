#!/usr/bin/env python2.2
# $Id: browse.py,v 1.2 2003/07/02 21:04:50 lsmithso Exp $
# Original by John OSullivan
# Mods by Les Smithson
#

from pymqi import QueueManager, Queue
from pymqi import cd, od, md, gmo
from pymqi import Error, MQMIError
import CMQC
import exceptions


    
def Browse( qname, qmname, box, port):
    qmgr = QueueManager( None)
    
    if box:
        channelDescr = cd( ChannelName="SVRCONN1", 
                           ConnectionName="%s(%s)" % ( box, port))
        
        #print channelDescr
        
        qmgr.connectWithOptions( qmname, channelDescr)
    else:
       qmgr.connect(qmname)
       
    gqdesc = od( ObjectName=qname)
    
    getq = Queue( qmgr, gqdesc, CMQC.MQOO_BROWSE)

    msgDesc = md()

    getOpts = gmo(Options = CMQC.MQGMO_BROWSE_NEXT)
    getOpts.WaitInterval = CMQC.MQWI_UNLIMITED
    
    print getOpts

    messages = []
    try:
        while 1:
            msg = getq.get(4194304, msgDesc, getOpts)
            date = msgDesc['PutDate']
            time = msgDesc['PutTime']
            sdate = "%s-%s-%s" % ( date[0:4], date[4:6], date[6:8])
            stime = "%s:%s:%s.%s" % ( time[0:2], time[2:4], time[4:6], time[6:8])
            messages.append( { 'date':sdate, 
                               'time':stime,
                               'app' :msgDesc['PutApplName'],
                               'msg' :msg})
            # null MsgId and CorrelId, or cursor won't move up
            # the Q
            msgDesc['MsgId'] = ''
            msgDesc['CorrelId'] = ''
    except MQMIError, me:
        pass
        
    return messages


if __name__ == '__main__':
    import sys
    nargs = len(sys.argv)
    if nargs < 2 or nargs > 5:
        print "Usage: python browse.py queue [queueManagerName [hostName port]]"
        sys.exit(1)
    qname   = sys.argv[1]
    box = port = None
    qmname = ''
    if nargs > 2:
        qmname  = sys.argv[2]
    if nargs > 3:
        box     = sys.argv[3]
        port    = sys.argv[4]    

    msgs = Browse( qname, qmname, box, port)
    for m in msgs:
	print "%s %s %s" % ( m['date'], m['time'], m['app'])        
        print m['msg']
        
