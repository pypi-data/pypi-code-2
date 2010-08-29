# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2009 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

'''
trosnoth.src.network.discoverymsg
This module defines the network messages used by the game discovery protocol.
The protocol is used to discover and broadcast information about Trosnoth games
running on the network and (if accessible) on the Internet.
'''

###########
# WARNING #
##############################################################################
# It is NOT A GOOD IDEA to modify the behaviour of this file too drastically #
# after the release of Trosnoth v1.1.0 because after this point there may be #
# games out there on the Internet which are using this protocol.             #
##############################################################################


import struct, socket
from trosnoth.src.network.netmsg import NetworkMessage, Message

class PeerRequestMsg(NetworkMessage):
    '''
    Asks to become a peer of the other server. Used when first connecting to
    an Internet server, and when needed to make up the number of peers.
    '''
    idString = 'gday'
    fields = 'port', 'idCode'
    packspec = 'I8s'

class AcceptPeerMsg(NetworkMessage):
    '''
    Used to indicate that the given host is accepted as a peer of this host.
    '''
    idString = 'yep.'
    fields = ()
    packspec = ''

class AlternativesMessage(Message):
    '''
    Superclass for messages which provides suggestions of other hosts to try
    to connect to. These should be hosts which are likely to be actually
    running (i.e. are peers of the current host). If these suggestions cannot
    be provided, host values of '0.0.0.0' should be used.
    '''
    fields = 'server1', 'server2', 'server3'

    def __init__(self, *args, **kwargs):
        # Initialise attributes based on arguments.
        Message.__init__(self, *args, **kwargs)

        # Check that packing can be performed.
        self.pack()

    def pack(self):
        '''
        Packs the field values of this message into a single string.
        '''
        return (
            self.idString +
            struct.pack('!4sI4sI4sI',
                socket.inet_aton(self.server1[0]),
                self.server1[1],
                socket.inet_aton(self.server2[0]),
                self.server2[1],
                socket.inet_aton(self.server3[0]),
                self.server3[1])
        )

    @classmethod
    def _build(cls, source):
        '''
        Called by buildMessage() to build an instance of this class from a
        network message string.
        '''
        ip1, port1, ip2, port2, ip3, port3 = struct.unpack('!4sI4sI4sI', source)
        return cls(
            (socket.inet_ntoa(ip1), port1),
            (socket.inet_ntoa(ip2), port2),
            (socket.inet_ntoa(ip3), port3),
        )


class DenyPeerMsg(AlternativesMessage):
    '''
    Used to indicate that the connecting host is not accepted as a peer of this
    host. This should only be sent if this host cannot connect via TCP to the
    remote host.
    '''
    idString = 'nope'

class LeavePeerMsg(AlternativesMessage):
    '''
    Used to indicate that this host no longer wishes to be a peer of the
    remote host.
    '''
    idString = 'bye.'

class QueryDataMsg(NetworkMessage):
    '''
    Sent to request information.

    This should only be sent by a host to a server if the host is unable to
    join as a peer, or when the host has first joined the peer network.
    '''
    idString = '?dat'
    fields = 'kind'
    packspec = '*'

class QueryCompleteMsg(NetworkMessage):
    '''
    Sent to indicate that the response to a data query is complete.
    '''
    idString = 'done'
    fields = ()
    packspec = ''

class RefuseQueryMsg(AlternativesMessage):
    '''
    Sent in response to a QueryDataMsg to indicate that the remote discoverer
    should try querying different servers instead.
    '''
    idString = 'ceas'

class ResetDataMsg(NetworkMessage):
    '''
    Used to indicate that the remote host should forget any data it already
    knew because this server is going to provide it with complete information.
    Sent in response to a QueryDataMsg before sending UpdateDataMsg.
    '''
    idString = 'rset'
    fields = ()
    packspec = ''


class UpdateDataMsg(Message):
    '''
    Sent to inform peers of updated data.
    '''
    idString = '+dat'
    fields = 'address', 'kind', 'key', 'value', 'certainty'
    certainty = 1.0     # Default

    def __init__(self, *args, **kwargs):
        # Initialise attributes based on arguments.
        Message.__init__(self, *args, **kwargs)

        # Check that packing can be performed.
        self.pack()

    def pack(self):
        '''
        Packs the field values of this message into a single string.
        '''
        return (
            self.idString +
            struct.pack('!4sIfII',
                socket.inet_aton(self.address[0]),
                self.address[1],
                self.certainty,
                len(self.kind),
                len(self.key)) +
            self.kind +
            self.key + 
            self.value
        )

    @classmethod
    def _build(cls, source):
        '''
        Called by buildMessage() to build an instance of this class from a
        network message string.
        '''
        size = struct.calcsize('!4sIfII')
        ipAddr, port, certainty, kindLen, keyLen = struct.unpack('!4sIfII', source[:size])
        sep1 = size + kindLen
        sep2 = sep1 + keyLen
        kind = source[size:sep1]
        key = source[sep1:sep2]
        value = source[sep2:]

        address = (socket.inet_ntoa(ipAddr), port)

        return cls(address, kind, key, value, certainty)

class DeleteDataMsg(Message):
    '''
    Sent to inform peers of deleted data.
    '''
    idString = '-dat'
    fields = 'address', 'kind', 'key', 'certainty'
    certainty = 1.0     # Default

    def __init__(self, *args, **kwargs):
        # Initialise attributes based on arguments.
        Message.__init__(self, *args, **kwargs)

        # Check that packing can be performed.
        self.pack()

    def pack(self):
        '''
        Packs the field values of this message into a single string.
        '''
        return (
            self.idString +
            struct.pack('!4sIfI',
                socket.inet_aton(self.address[0]),
                self.address[1],
                self.certainty,
                len(self.kind)) +
            self.kind +
            self.key
        )

    @classmethod
    def _build(cls, source):
        '''
        Called by buildMessage() to build an instance of this class from a
        network message string.
        '''
        size = struct.calcsize('!4sIfI')
        ipAddr, port, certainty, kindLen = struct.unpack('!4sIfI',
                source[:size])
        sep1 = size + kindLen
        kind = source[size:sep1]
        key = source[sep1:]

        address = (socket.inet_ntoa(ipAddr), port)

        return cls(address, kind, key, certainty)

class ConfirmDataMsg(NetworkMessage):
    '''
    Sent to confirm information that is being checked with a VerifyDataMsg.
    '''
    idString = 'hav.'
    fields = 'value'
    packspec = '*'

class DenyDataMsg(NetworkMessage):
    '''
    Sent to deny information that is being checked with a VerifyDataMsg.
    '''
    idString = 'hvnt'
    fields = ()
    packspec = ''

class VerifyDataMsg(Message):
    '''
    Sent to check information with its source.
    '''
    idString = 'hav?'
    fields = 'kind', 'key'

    def __init__(self, *args, **kwargs):
        # Initialise attributes based on arguments.
        Message.__init__(self, *args, **kwargs)

        # Check that packing can be performed.
        self.pack()

    def pack(self):
        '''
        Packs the field values of this message into a single string.
        '''
        return (
            self.idString +
            struct.pack('!I', len(self.kind)) +
            self.kind +
            self.key
        )

    @classmethod
    def _build(cls, source):
        '''
        Called by buildMessage() to build an instance of this class from a
        network message string.
        '''
        size = struct.calcsize('!I')
        kindLen, = struct.unpack('!I', source[:size])
        sep1 = size + kindLen
        kind = source[size:sep1]
        key = source[sep1:]

        return cls(kind, key)

class DiagnosticRequestMsg(NetworkMessage):
    '''
    Sent to request diagnostic information from the server.
    '''
    idString = 'dvlg'
    fields = ()
    packspec = ''

class DiagnosticResponseMsg(Message):
    '''
    Send in response to a DiagnosticRequestMsg.
    '''
    idString = 'here'
    fields = 'agent', 'peerCount', 'peer1', 'peer2', 'peer3', 'peer4', 'peer5'

    def __init__(self, *args, **kwargs):
        # Initialise attributes based on arguments.
        Message.__init__(self, *args, **kwargs)

        # Check that packing can be performed.
        self.pack()

    def pack(self):
        '''
        Packs the field values of this message into a single string.
        '''
        return (
            self.idString +
            struct.pack('!I4sI4sI4sI4sI4sI',
                self.peerCount,
                socket.inet_aton(self.peer1[0]),
                self.peer1[1],
                socket.inet_aton(self.peer2[0]),
                self.peer2[1],
                socket.inet_aton(self.peer3[0]),
                self.peer3[1],
                socket.inet_aton(self.peer4[0]),
                self.peer4[1],
                socket.inet_aton(self.peer5[0]),
                self.peer5[1],
            ) + self.agent
        )

    @classmethod
    def _build(cls, source):
        '''
        Called by buildMessage() to build an instance of this class from a
        network message string.
        '''
        size = struct.calcsize('!I4sI4sI4sI4sI4sI')
        peerCount, ip1, port1, ip2, port2, ip3, port3, ip4, port4, ip5, port5 = \
                struct.unpack('!I4sI4sI4sI4sI4sI', source[:size])
        return cls(
            source[size:],
            peerCount,
            (socket.inet_ntoa(ip1), port1),
            (socket.inet_ntoa(ip2), port2),
            (socket.inet_ntoa(ip3), port3),
            (socket.inet_ntoa(ip4), port4),
            (socket.inet_ntoa(ip5), port5),
        )
