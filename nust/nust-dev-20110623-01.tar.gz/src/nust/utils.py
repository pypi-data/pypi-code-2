#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function 

import socket
import struct 

#---------------------------------------------------------------
#---------------------------------------------------------------
def ping_uwsgi(sock_file):
    '''
    Ping UWSGI process trought socket. Return [True,...] if OK,
    return [False,error] if UWSGO not pinging, or
    [None,error] if common error (ex. socket file not found)
    '''
    rv = [None,'']
    fmt_h = str('<BHB')
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.connect(sock_file)
    except socket.error,e:
    	rv = [None,e]
	sock = None
    if (sock):
        ping = struct.pack(fmt_h,100,0,0)
        sock.send(ping)
        pong = sock.recv(struct.calcsize(fmt_h))
        sock.close()
        p = struct.unpack(fmt_h,pong)
	if (p == (100,0,1)):
	    rv = [True, 'OK']
	else:
	    rv = [False, 'ERR']
    return rv
#---------------------------------------------------------------
#---------------------------------------------------------------
