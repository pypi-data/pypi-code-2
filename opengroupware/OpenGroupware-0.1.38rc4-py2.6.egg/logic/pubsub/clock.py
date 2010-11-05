#
# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#
import time
from coils.foundation import *
from coils.core       import *

class ClockService(Service):
    __service__       = 'coils.clock'
    __auto_dispatch__ = True
    __is_worker__     = True
    
    def __init__(self):
        Service.__init__(self)

    def prepare(self):
        self._subscribers = [ ]
        self._ctx = AnonymousContext()
        self._ticktock = time.time()
        Service.prepare(self)

    @property
    def ticktock(self):
        if ((time.time() - self._ticktock) > 59):
            self._ticktock = time.time()
            return True
        return False

    @property
    def subscribers(self):
        return self._subscribers

    @property
    def stamp(self):
        x = self._ctx.get_utctime()
        return '{0} {1}'.format(x.strftime('%Y %m %d %H %M %w %a %b'),
                                 int(time.mktime(x.timetuple())))

    def do_subscribe(self, parameter, packet):
        if (packet.source not in self.subscribers):
            self.subscribers.append(packet.source)
        self.send(Packet.Reply(packet, self.stamp))

    def do_unsubscribe(self, parameter, packet):
        if (packet.source in self.subscribers):
            self.subscribers.remove(packet.source)
        self.send(Packet.Reply(packet, self.stamp))

    def work(self):
        if (self.ticktock):
            x = self.stamp
            for target in self.subscribers:
                self.send(Packet('coils.clock/__null', target, x))
