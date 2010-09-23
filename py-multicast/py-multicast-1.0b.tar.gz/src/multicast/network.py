#!/bin/env python

import socket
import struct
import fcntl
import array

SIOCGIFCONF = 0x8912
SIOCGIFFLAGS = 0x8913

IFF_MULTICAST = 0x1000   

def ifconfig():
    """
    Fetch network stack configuration.
    """

    class _interface:
        def __init__(self, name):
            self.name = name
            self.addresses = []
            self.up = False
            self.multicast = False

        def _first_ip(self):
            try:
                return self.addresses[0]
            except IndexError:
                return None
        ip = property(_first_ip)
    
    #Get the list of all network interfaces
    _socket = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
    buffer = array.array ( 'B', '\0' * 4096 )
    reply_length = struct.unpack ( 'iL', fcntl.ioctl(_socket.fileno(), SIOCGIFCONF, struct.pack ('iL', 4096, buffer.buffer_info()[0])))[0]
    if_list = buffer.tostring()    
    if_list = filter(lambda x: len(x[0]) > 0, [ (if_list[i:i+32].split('\0', 1)[0], socket.inet_ntoa(if_list[i+20:i+24])) for i in range(0, 4096, 32)])
    
    iff = {}
    
    #Get ip addresses for each interface
    for (ifname, addr) in if_list:
        iff[ifname] = iff.get (ifname, _interface(ifname) );
        flags, = struct.unpack ( 'H', fcntl.ioctl(_socket.fileno(), SIOCGIFFLAGS, ifname + '\0'*256)[16:18])
        iff[ifname].addresses.append ( addr )
        iff[ifname].up = bool(flags & 1)
        iff[ifname].multicast = bool(flags & IFF_MULTICAST)
        
    _socket.close()
    return iff


