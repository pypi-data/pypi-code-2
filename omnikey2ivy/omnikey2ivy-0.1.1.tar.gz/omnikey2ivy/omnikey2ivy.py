#!/usr/bin/python


#  adapted from readmifare1k.py of Adam Laurie <adam@algroup.co.uk>,
#  http://rfidiot.org/
# 
#  This code is copyright (c) ENAC, 2011, All rights reserved.
#  For non-commercial use only, the following terms apply - for all other
#  uses, please contact the author:
#
#    This code is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#


import sys
import os
import time
import getopt

from ivy.std_api import *
import RFIDIOt.RFIDIOtconfig as RFIDIOtconfig





def connect_to_ivy():
    IVYAPPNAME = "RFIDCardReader"
    # initializing ivybus and isreadymsg
    sivybus = ""
    sisreadymsg = "[%s is ready]" % IVYAPPNAME
    # getting option
    try:
            optlist, left_args = getopt.getopt(sys.argv[1:],'hb:', ['ivybus='])
    except getopt.GetoptError:
            # print help information and exit:
            usage(sys.argv[0])
            sys.exit(2)
    for o, a in optlist:
            if o in ("-h", "--help"):
                    usage(sys.argv[0])
                    sys.exit()
            elif o in ("-b", "--ivybus"):
                    sivybus= a
    if sivybus != "" :
            sechoivybus = sivybus
    elif os.environ.has_key("IVYBUS"):
            sechoivybus = os.environ["IVYBUS"]
    else:
            sechoivybus = "ivydefault"
    print "Ivy will broadcast on %s "%sechoivybus

    # initialising the bus 
    IvyInit(IVYAPPNAME,   # application name for Ivy
                    sisreadymsg , # ready message
                    0,            # main loop is local (ie. using IvyMainloop)
                    lambda a,c:0,     # handler called on connection/deconnection
                    lambda a,i:0     # handler called when a diemessage is received 
                    )
    # starting the bus
    # Note: env variable IVYBUS will be used if no parameter or empty string
    # is given ; this is performed by IvyStart (C)
    IvyStart(sivybus)
    
def run():
    uid = "";
    delay=.1
    try:
        card= RFIDIOtconfig.card
    except:
        print "fail to connect with card reader" #FIXME should use stderr
        os._exit(True)
    connect_to_ivy()
    
    while True:
        card.select()
        if card.uid == uid :
            time.sleep(delay)
        else:
            uid = card.uid
            if uid:
                print  'Card ID: ' + card.uid
                IvySendMsg("Id %s" % card.uid)
            else:
                print 'No card'


if __name__=="__main__":
    run()
