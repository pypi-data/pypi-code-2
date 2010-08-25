# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
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
# THE SOFTWARE.
#
import sys, logging, os, yaml
from multiprocessing import Pipe
from packet          import Packet
from broker          import Broker
from coils.foundation import ServerDefaultsManager

class Service(object):
    __auto_dispatch__  = False
    __is_worker__      = False
    __AMQDebugOn__     = None
    __ServiceDebugOn__ = None
    __TimeOut__        = 10

    def __init__(self):
        self._shutdown = False
        if (Service.__AMQDebugOn__ is None):
            sd = ServerDefaultsManager()
            Service.__AMQDebugOn__ = sd.bool_for_default('BusDebugEnabled')
        if (Service.__ServiceDebugOn__ is None):
            sd = ServerDefaultsManager()
            Service.__ServiceDebugOn__  = sd.bool_for_default('ServiceDebugEnabled')

    @property
    def amq_debug(self):
        return Service.__AMQDebugOn__

    @property
    def service_debug(self):
        return Service.__ServiceDebugOn__

    @property
    def broker(self):
        return self._broker

    def setup(self, silent=True):
        if (silent):
            sys.stdin  = open('/dev/null', 'r')
            sys.stdout = open('/dev/null', 'w')
            sys.stderr = open('/dev/null', 'w')
        self._pid = os.getpid()
        self._broker = Broker()
        self.log = logging.getLogger('{0}[{1}]'.format(self.__service__, os.getpid()))
        self._broker.subscribe(self.__service__, self.receive_message)

    def send(self, packet):
        if (self.amq_debug):
            self.log.debug('Sending {0} to {1}'.format(packet.uuid, packet.target))
        self._broker.send(packet)

    def shutdown(self):
        if (self.service_debug):
            self.log.debug('{0} PID#{1} shutting down.'.format(self.__service__, os.getpid()))
        if (self.amq_debug):
            self.log.debug('Shutting down AMQ broker.')
        self._broker.close()
        if (self.amq_debug):
            self.log.debug('AMQ broker is shutdown.')
        sys.exit(0)

    def receive_message(self, message):
        packet = self._broker.packet_from_message(message)
        if (packet is not None):
            if (self.amq_debug):
                self.log.debug('received {0} from {1}'.format(packet.uuid, packet.source))
            method    = Packet.Method(packet.target).lower()
            parameter = Packet.Parameter(packet.target)
            response = self.process(method, parameter, packet)
            if (response is not None):
                self.send(response)

    def wait(self, timeout=None):
        self._broker.wait(timeout)

    def prepare(self):
        try:
            import procname
            procname.setprocname('service::{0}'.format(self.__service__))
        except:
            self.log.info('Failed to set process name for service')
        packet = Packet('{0}/__hello_ack'.format(self.__service__),
                        'coils.master/__hello', self.__service__)
        self.hello_uuid = packet.uuid
        self.send(packet)
        if (self.amq_debug or self.service_debug):
            self.log.debug('Hello packet sent to master,')

    def process(self, method, parameter, packet):
        if (self.amq_debug or self.service_debug):
            self.log.debug('Processing message.')
        if ((method == '__ping') or (method == '__hello')):
            # From a services point of view a ping and a hello are the same thing.
            return Packet.Reply(packet, packet.data)
        elif (method == '__hello_ack'):
            # A hello ack should be in reply to our hello and have as data
            # the name of ourselves.
            if ((self.hello_uuid == packet.reply_to) and
                (str(packet.data) == self.__service__)):
                if (self.amq_debug or self.service_debug):
                    self.log.debug('Recevied valid Hello ACK from {0}'.format(packet.source))
            else:
                pass
        elif (method == '__null'):
                pass
        elif (method == '__shutdown'):
                self.shutdown()
        elif (self.__auto_dispatch__):
            if (self.service_debug):
                self.log.debug('Auto message dispatch enabled')
            method = 'do_{0}'.format(method)
            if (hasattr(self, method)):
                if (self.amq_debug or self.service_debug):
                    self.log.debug('Invoking method: {0}'.format(method))
                return getattr(self, method)(parameter, packet)
            else:
                if (self.service_debug):
                    self.log.error('Service has no such method as {0}'.format(method))
        return None

    def work(self):
        pass

    def run(self, silent=True):
        self.setup(silent=silent)
        self.prepare()
        if (self.service_debug):
            self.log.debug('Entering event loop.')
        while (not self._shutdown):
            self.wait(timeout=self.__TimeOut__)
            self.work()
