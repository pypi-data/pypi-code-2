# DjangoDE, an integrated development environment for Django
# Copyright (C) 2010-2011 Andrew Wilkinson
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import socket
import struct
import pickle

_msg_sock = None

def connect_to_editor(port):
    global _msg_sock

    _msg_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _msg_sock.connect(('localhost', port+1))

def send_msg(*args):
    msg = pickle.dumps(args)
    _msg_sock.sendall(struct.pack("i", len(msg)) + msg)

    resp = _msg_sock.recv(struct.calcsize("i"))
    size, = struct.unpack("i", resp)

    if size > 0:
        resp = _msg_sock.recv(size)
        print resp
        return pickle.loads(resp)
    else:
        return None
