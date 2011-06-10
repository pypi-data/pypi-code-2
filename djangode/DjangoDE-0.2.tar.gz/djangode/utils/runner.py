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

import atexit
import logging
import os
import pickle
import random
import struct
import socket
import subprocess
import sys
import threading
import time

from djangode import global_objects

logger = logging.getLogger("djangode.utils.runner")

class Runner(object):
    def __init__(self, manage_file):
        self.manage_file = manage_file

        self._port = random.choice(range(8001, 10000))
        self._process = None
        self._socket = None
        self._listener = None

    def __del__(self):
        self.stop()

    def start(self):
        if global_objects.project is None or self.is_running():
            return

        self._port = random.choice(range(8001, 10000))

        self._listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._listener.bind(('localhost', self._port+2))
        self._listener.listen(1)

        thread = threading.Thread(target=runner_receiver, args=(self._listener, ))
        thread.daemon = True
        thread.start()

        old_cwd = os.getcwd()
        os.chdir(os.path.dirname(self.manage_file))

        logger.info("Starting runner for %s", self.manage_file)
        try:
            if global_objects.project.settings.get("pre_runserver_command", "") != "":
                self._process = subprocess.Popen(["%s && djangode-runner %s %i" % (global_objects.project.settings["pre_runserver_command"], self.manage_file, self._port)], shell=True)
            else:
                self._process = subprocess.Popen(["djangode-runner", self.manage_file, str(self._port)])
        except OSError, e:
            logger.error("Failed to start djangode-runner. Got error '%s'." % (unicode(e), ))
            return False

        os.chdir(old_cwd)

        atexit.register(self.stop)

        return True

    def stop(self):
        if not self.is_running():
            return

        logger.info("Stopping runner for %s", self.manage_file)
        if self._socket is not None:
            self._socket.close()
            self._socket = None
        if self._listener is not None:
            self._listener.close()
            self._listener = None

        self._process.terminate()
        self._process.wait()
        self._process = None
        logger.info("Stopped runner for %s", self.manage_file)

    def send_message(self, *args, **kwargs):
        if not self.connect():
            raise RunnerStopped

        msg = pickle.dumps(args)
        logger.debug(repr(struct.pack("i", len(msg)) + msg))
        self._socket.sendall(struct.pack("i", len(msg)) + msg)

        resp = self._socket.recv(struct.calcsize("i"))

        if resp == "":
            self.stop()
            if kwargs.get("attempt", 0) == 5:
                raise RunnerStopped
            else:
                self.start()

                return self.send_message(*args, **{ "attempt": kwargs.get("attempt", 0) + 1 })

        try:
            size, = struct.unpack("i", resp)
        except struct.error:
            raise RunnerError, "Invalid reply from runner. Got %s" % (repr(resp), )

        if size > 0:
            return pickle.loads(self._socket.recv(size))
        else:
            return None

    def connect(self):
        if self._socket is not None:
            return True

        if not self.is_running() and not self.start():
            return False

        failure_count = 0

        while True:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self._socket.connect(("localhost", self._port+1))
            except socket.error, e:
                if e.errno == 111 and failure_count < 10: # Connection refused
                    failure_count += 1
                    time.sleep(1)
                    continue
                else:
                    self._socket = None
                    logger.error("Failed to connect to djangode-runner back channel. %s. " % (unicode(e), ))
                    return False
            else:
                return True

    def is_running(self):
        if self._process is None:
            return False
        else:
            self._process.poll()
            return self._process.returncode is None

    def host(self):
        return "http://127.0.0.1:%i" % (self._port, )

def runner_receiver(socket):
    conn, add = socket.accept()

    try:
        size = struct.calcsize("i")

        while True:
            msg_size = conn.recv(size)
            if msg_size == "":
                break

            msg_size, = struct.unpack("i", msg_size) # pylint: disable-msg=E1101

            msg = pickle.loads(conn.recv(msg_size)) # pylint: disable-msg=E1101

            if msg[0] == "debug":
                resp = global_objects.project.debug(*msg[1:])
            else:
                logging.error("Unable to handle message %s." % (msg[0], ))
                resp = "done"

            conn.send(struct.pack("i", len(pickle.dumps(resp))) + pickle.dumps(resp))
    finally:
        conn.close()
        socket.close()

class RunnerError(Exception):
    pass

class RunnerStopped(Exception):
    pass
