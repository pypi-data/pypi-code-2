# DjangoDE, an integrated development environment for Django
# Copyright (C) 2010 Andrew Wilkinson
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

import imp
import os
import threading
import traceback
import pickle
import socket
import struct
import sys

from django.core.management import execute_manager

from debugger import Debugger, continue_running, set_breakpoints
from get_urls import get_urls
from get_settings_names import get_settings_names
from get_setting_value import get_setting_value
from module_contents import module_contents, module_file
from send_msg import connect_to_editor

python_suffix = [s for s in imp.get_suffixes() if s[0] == ".py"][0]

def main():
    manage_file = sys.argv[1]

    sys.path.insert(0, os.path.dirname(manage_file))

    Debugger.instance = Debugger()

    threading.Thread(target=control_thread, args=(int(sys.argv[2]) + 1, )).start()

    sys.argv[1] = "runserver"
    sys.argv[2] = "localhost:%i" % (int(sys.argv[2]), )
    sys.argv.append("--noreload")

    imp.load_module("manage", open(manage_file, python_suffix[1]), manage_file, python_suffix)

    import settings # pylint: disable-msg=F0401
    Debugger.instance.runcall(execute_manager, settings)

def control_thread(port):
    connect_to_editor(port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("localhost", port))
    except socket.error, e:
        if e.errno == 98:
            print "Error connecting to port, %i. Already in use." % (port, )
        else:
            raise
    sock.listen(1)

    conn, addr = sock.accept()

    try:
        size = struct.calcsize("i")

        while True:
            msg = conn.recv(size)
            if msg == "":
                break
            msg_size, = struct.unpack("i", msg) # pylint: disable-msg=E1101
            msg = pickle.loads(conn.recv(msg_size)) # pylint: disable-msg=E1101

            try:
                if msg[0] == "get_urls":
                    resp = get_urls()
                elif msg[0] == "get_settings_names":
                    resp = get_settings_names()
                elif msg[0] == "get_setting_value":
                    resp = get_setting_value(msg[1])
                elif msg[0] == "continue_running":
                    resp = continue_running()
                elif msg[0] == "set_breakpoints":
                    resp = set_breakpoints(msg[1])
                elif msg[0] == "module_contents":
                    resp = module_contents(msg[1])
                elif msg[0] == "module_file":
                    resp = module_file(msg[1])
                elif msg[0] == "get_pythonpath":
                    resp = sys.path
                else:
                    resp = ("done", )
            except:
                traceback.print_exc()
                conn.sendall(struct.pack("i", 0))
                continue

            msg = pickle.dumps(resp)
            conn.sendall(struct.pack("i", len(msg)) + msg) # pylint: disable-msg=E1101
    finally:
        conn.close()
        sock.close()

