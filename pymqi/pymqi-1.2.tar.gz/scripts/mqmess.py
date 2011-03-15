#!/usr/bin/env python2.2
# $Id: mqmess.py,v 1.2 2003/07/02 21:04:37 lsmithso Exp $
# Display the mnemonic for an MQ reason code. Completion code is
# assumed to be error, regardless of reaason code. 
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

import pymqi, sys


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: mqmess reason [reason1,..., reasonN]'
        sys.exit(-1)
    else:
        for r in sys.argv[1:]:
            e = pymqi.MQMIError(2, int(r))
            print str(e)
            

