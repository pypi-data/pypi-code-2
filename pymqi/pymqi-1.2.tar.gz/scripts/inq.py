#!/usr/bin/env python2.2
# $Id: inq.py,v 1.3 2003/07/02 21:04:23 lsmithso Exp $
# Silly thing to Inquire on all that is enquirable on a Queue Manager
# & Queue.
#
# Author: L. Smithson (lsmithson@open-networks.co.uk)
#
# DISCLAIMER
# You are free to use this code in any way you like, subject to the
# Python & IBM disclaimers & copyrights. I make no representations
# about the suitability of this software for any purpose. It is
# provided "AS-IS" without warranty of any kind, either express or
# implied. So there.
#
#

import pymqi, CMQC, sys, string


if __name__ == '__main__':
    if len(sys.argv) > 1:
        qName = sys.argv[1]
    else:
        qName = 'QTEST1'
    print 'Using qname', qName
 
    # Build a list of all MQ defs that begin with MQIA or MQCA.
    attrList = []
    for i in CMQC.__dict__.keys():
        if i[0:5] == 'MQIA_' or i[0:5] == 'MQCA_':
            attrList.append(i)
    # Inquire on all things QueueManagery
    # Defaults to queue manager named ''
    qMgr = pymqi.QueueManager()
    inqQ = pymqi.Queue(qMgr, qName)
    for o in (qMgr, inqQ):
        for i in attrList:
            try:
                val = o.inquire(eval('CMQC.' + i))
                print '%s -- %s: %s' % (o.__class__.__name__, i, val)
            except: 
                pass
            
        
            

