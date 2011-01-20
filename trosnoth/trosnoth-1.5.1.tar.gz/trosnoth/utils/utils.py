# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2011 Joshua D Bartlett
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

import logging

def new(count):
    '''new(count) - returns an iterator object which will give count distinct
    instances of the object class.  This is useful for defining setting
    options.  For example, north, south, east, west = new(4) . There is no
    reason that these options should be given numeric values, but it is
    important that north != south != east != west.
    '''
    for i in xrange(count):
        yield object()

# timeNow is used to update things based on how much time has passed.
# Note: on Windows, time.clock() is more precise than time.time()
# On Windows time.clock() also does not change when the system clock changes.
# On linux however, time.clock() measures process time rather than wall time.
import platform
if platform.system() == 'Windows':
    from time import clock as timeNow
else:
    from time import time as timeNow

from hashlib import sha1 as hasher

class RunningAverage(object):
    def __init__(self, count):
        self.values = []
        self.total = 0.
        self.maxCount = count

    @property
    def mean(self):
        if len(self.values) == 0:
            return None
        return self.total / len(self.values)

    def noteValue(self, value):
        self.total += value
        self.values.append(value)
        if len(self.values) > self.maxCount:
            self.total -= self.values.pop(0)


def initLogging(debug=False, logFile=None):
    import twisted.python.log
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    if logFile:
        logging.getLogger().addHandler(logging.FileHandler(logFile))
    observer = twisted.python.log.PythonLoggingObserver()
    observer.start()
