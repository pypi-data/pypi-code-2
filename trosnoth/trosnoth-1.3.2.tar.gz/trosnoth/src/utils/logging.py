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

import sys
import os
import traceback
import time

from trosnoth.data import getPath, user, makeDirs

def startLogging(subdir = None):
    'initialises the debug module.'
    global logFile
    global oldOut
    global oldErr

    if subdir is not None:
        directory = getPath(user, 'logs', subdir)
    else:
        directory = getPath(user, 'logs')

    makeDirs(directory)

    i = 0
    while True:
        fname = 'log%03d.txt' % i
        fname = os.path.join(directory, fname)
        if not os.path.exists(fname):
            break
        i += 1

    logFile = file(fname, 'w')
    oldOut, oldErr = sys.stdout, sys.stderr
    sys.stdout = MultipleWriter(oldOut, logFile)
    sys.stderr = MultipleWriter(oldErr, logFile)

def endLogging():
    logFile.flush()
    logFile.close()
    sys.stdout = oldOut
    sys.stderr = oldErr

class MultipleWriter(object):
    def __init__(self, *streams):
        self.streams = streams
        
    def write(self, thing):
        if thing == '\n':
            return

        for stream in self.streams:
            if stream is sys.__stdout__ or sys.__stderr__ in self.streams:
                print >> stream, thing.rstrip()
            else:
                print >> stream, "[%s] %s" % \
                      (time.strftime("%Y-%m-%d %H:%M:%S"), thing.rstrip())
                
def writeException():
    print >> sys.stderr, ' '
    tb = sys.exc_info()[2]
    print >> sys.stderr, 'Exception caught in file %r, line %d, in %s' % (tb.tb_frame.f_code.co_filename, tb.tb_frame.f_lineno, tb.tb_frame.f_code.co_name)
    traceback.print_exc()
