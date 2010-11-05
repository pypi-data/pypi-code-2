# -*- coding: utf-8 -*-

''' PyTTY - Python serial access package '''

__credits__ = '''Copyright (C) 2010 Arc Riley

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU Lesser General Public License as published
  by the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.

  You should have received a copy of the GNU Lesser General Public License
  along with this program; if not, see http://www.gnu.org/licenses
'''
__author__  = 'Arc Riley <arcriley@gmail.com>'

import io

class TTY (io.BufferedRWPair) :
  ''' TTY io class

    This is a subclass of io.BufferedRWPair from the Python standard library 
    which opens a tty device, sets nonblock mode on the device, and allows the
    user to change baud rate, flow control, and other settings often available 
    to tty devices.
  '''

  _iobase = io.FileIO

  def __init__ (self, name) :
    from fcntl import fcntl, F_SETFL, F_GETFL
    from os import O_NONBLOCK

    reader = self._iobase(name, 'r')

    # ensure this is actually a tty device
    if not reader.isatty() :
      raise IOError('%s is not a tty device' % name)

    # set non-blocking mode on the reader
    fd = reader.fileno()
    fcntl(fd, F_SETFL, (fcntl(fd, F_GETFL) | O_NONBLOCK))

    # open a separate writer device
    writer = self._iobase(name, 'w')

    # set non-blocking mode on the reader
    fd = reader.fileno()
    fcntl(fd, F_SETFL, (fcntl(fd, F_GETFL) | O_NONBLOCK))

    # initialize self with BufferedRWPair 
    super(TTY, self).__init__(reader, writer)


# Clean up package namespace
del(io)

