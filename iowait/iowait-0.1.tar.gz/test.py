# Copyright (C) 2011  Andrea Corbellini
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import select
import socket
import sys
import time
import unittest
import iowait


# Create a test message that works with both Python 2 and 3.
try:
    TEST_DATA = bytes('Hello world', 'ascii')
except TypeError:
    TEST_DATA = 'Hello world'


if hasattr(socket, 'socketpair'):
    socketpair = socket.socketpair
else:
    # Work-around for operating systems that don't define socketpair().
    test_server = None

    def socketpair():
        global test_server
        if test_server is None:
            test_server = socket.socket()
            test_server.bind(('localhost', 12345))
            test_server.listen(1)

        sock_a = socket.create_connection(('localhost', 12345))
        sock_b = test_server.accept()[0]
        return sock_a, sock_b


class IOWaitTestCase(unittest.TestCase):

    def test_iowait(self):
        self._perform_test(iowait.IOWait)

    def test_selectiowait(self):
        self._perform_test(iowait.SelectIOWait)

    def test_polliowait(self):
        if hasattr(select, 'poll'):
            self.assertTrue(iowait.PollIOWait.available)
            self._perform_test(iowait.PollIOWait)
        else:
            self.assertFalse(iowait.PollIOWait.available)

    def test_epolliowait(self):
        if hasattr(select, 'epoll'):
            self.assertTrue(iowait.EPollIOWait.available)
            self._perform_test(iowait.EPollIOWait)
        else:
            self.assertFalse(iowait.EPollIOWait.available)

    def test_kqueueiowait(self):
        if hasattr(select, 'kqueue'):
            self.assertTrue(iowait.KQueueIOWait.available)
            self._perform_test(iowait.KQueueIOWait)
        else:
            self.assertFalse(iowait.KQueueIOWait.available)

    def _perform_test(self, cls):
        waitobj = cls()
        # Calling wait() now should raise ValueError.
        self.assertRaises(ValueError, waitobj.wait)

        a, b = socketpair()
        # Use the socket as unblocking, so that every attempt to use the socket
        # when it's not ready will fail.
        a.setblocking(False)
        b.setblocking(False)

        # Passing an invalid file object or not specifying read/write should
        # result in a TypeError and a ValueError respectively.
        self.assertRaises(TypeError, waitobj.watch, [object()], {'read': True})
        self.assertRaises(ValueError, waitobj.watch, [a])

        # Wait for the socket to be ready to send.
        waitobj.watch(a, write=True)
        events = waitobj.wait()
        self.assertEqual(events, [(a, False, True)])

        # Send some data.
        a.sendall(TEST_DATA)

        # Unregister the first socket.
        waitobj.unwatch(a)
        # Calling wait() should raise ValueError.
        self.assertRaises(ValueError, waitobj.wait)

        # Register the other socket and wait for it to be ready to receive.
        waitobj.watch(b, read=True)
        events = waitobj.wait()
        self.assertEqual(events, [(b, True, False)])

        # Read some data, but without consuming the whole buffer.
        b.recv(5)
        # wait() should still say that the socket is ready to receive data.
        events = waitobj.wait()
        self.assertEqual(events, [(b, True, False)])

        # Consume all the data. wait() should now hang. For this reason a
        # timeout of 0.5 seconds is specified.
        b.recv(1024)
        events = waitobj.wait(.5)
        # wait() should return an empty iterator.
        self.assertEqual(events, [])

        # Register the socket again, but listening for both read and write
        # events.
        waitobj.watch(b, read=True, write=True)
        events = waitobj.wait()
        self.assertEqual(events, [(b, False, True)])

        # Sending data to the socket will result in both a read and a write
        # event.
        a.setblocking(False)
        a.sendall(TEST_DATA)
        if sys.platform == 'win32':
            # For some odd reason, Windows needs some time to realize that the
            # test data has been sent through the socket.
            time.sleep(0.5)
        events = waitobj.wait()
        self.assertEqual(events, [(b, True, True)])


if __name__ == '__main__':
    unittest.main()
