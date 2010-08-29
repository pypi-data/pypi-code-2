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

from trosnoth.src.utils.components import Component, Plug
from trosnoth.src.utils.utils import timeNow
from trosnoth.src.utils.event import Event
from trosnoth.src.network.client import clientMsgs
from trosnoth.src.network.netmsg import MessageTypeError
import base64


# Remove the newline character at the end, since we never care
def getLine(file):
    line = file.readline()
    if (line.endswith('\n')):
        return line[:len(line)-1]
    return line



class ReplayRecorder(Component):
    inPlug = Plug()

    FLUSH_AFTER = 20
    def __init__(self, filename):
        Component.__init__(self)
        self.filename = filename
        self.file = open(self.filename, 'w')
        self.numTilFlush = self.FLUSH_AFTER
        self.timeStarted = timeNow()
        self.stopped = False

    def timeStamp(self):
        return timeNow() - self.timeStarted

    @inPlug.defaultHandler
    def gotMessage(self, msg):
        if self.stopped:
            return
        datagram = base64.b64encode(msg.pack())
        string = '%#.3f %s\n' % (self.timeStamp(), datagram)
        self.file.write(string)
        self.numTilFlush -= 1
        if self.numTilFlush <= 0:
            self.numTilFlush = self.FLUSH_AFTER
            self.file.flush()

    def stop(self):
        self.file.flush()
        self.file.close()
        self.stopped = True

from twisted.internet import reactor

# Emulates a normal server by outputting the same messages that a server once did
class ReplayPlayer(Component):
    inPlug = Plug()
    outPlug = Plug()

    MESSAGES_TO_LOAD = 500
    MINIMUM_MESSAGES = 150
    def __init__(self, filename):
        Component.__init__(self)
        self.file = open(filename, 'r')
        self.messagesToReplay = []
        self.finished = False
        self.paused = True
        self.onFinished = Event()


    def begin(self):
        self.paused = False
        self.loadMessages(self.MESSAGES_TO_LOAD)
        self.timeStarted = timeNow()
        reactor.callLater(0, self.tick)


    def loadMessages(self, number):
        assert not self.finished
        for i in range(0, number):
            line = getLine(self.file)
            if line == '':
                self.finished = True
                break
            try:
                s_time, encoded = line.split(' ', 2)
                time = float(s_time)
                datagram = base64.b64decode(encoded)
                msg = clientMsgs.buildMessage(datagram)
            except MessageTypeError:
                print 'WARNING: UNKNOWN MESSAGE: %s' % (datagram,)
            except:
                print 'WARNING:  UNKNOWN LINE: %s' % (line,)
            else:
                self.messagesToReplay.append((time, msg))
            

    def tick(self):
        if self.paused:
            return
        timePassed = timeNow() - self.timeStarted
        while len(self.messagesToReplay) > 0:
            time, msg = self.messagesToReplay[0]
            if time <= timePassed:
                self.outPlug.send(msg)
                del self.messagesToReplay[0]
            else:
                break
        if not self.finished and len(self.messagesToReplay) < self.MINIMUM_MESSAGES:
            self.loadMessages(self.MESSAGES_TO_LOAD - len(self.messagesToReplay))
            
        if len(self.messagesToReplay) == 0 and self.finished:
            self.onFinished.execute()
        else:
            reactor.callLater(0, self.tick)

    def pause(self):
        self.paused = True
        self.timePaused = timeNow()

    def unpause(self):
        self.paused = False
        # Reset the reference time, adding the duration that we were paused
        self.timeStarted += (timeNow() - self.timePaused)
        
