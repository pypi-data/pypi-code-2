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
from time             import time
from coils.core       import *
from process          import Process as WFProcess
import multiprocessing

def start_workflow_process(p, c):
    w = WFProcess(p, c)
    w.run()


class ExecutorService(Service):
    __service__ = 'coils.workflow.executor'
    __auto_dispatch__ = True
    __is_worker__     = False

    def __init__(self):
        Service.__init__(self)

    def prepare(self):
        Service.prepare(self)
        self._workers = { }
        self.send(Packet('coils.workflow.executor/ticktock',
                         'coils.clock/subscribe',
                         None))


    def _start_a_queued_process(self):
        self.send(Packet('coils.workflow.executor/__null',
                         'coils.workflow.queueManager/checkQueue:{0}'.format(len(self._workers)),
                         None))
                         
    def _start_process(self, process_id, context_id):
        self.log.debug('Attempting to start/restart processId#{0}'.format(process_id))
        if (process_id in self._workers):
            # TODO: Signal the route, maybe it wants to check for new messages?
            self.log.info('Received start signal for already running process.')
            return
        s, r = multiprocessing.Pipe()
        p = multiprocessing.Process(target=start_workflow_process,
                                    args=(process_id, context_id))
        self._workers[process_id] = { 'process':   p,
                                      'status':    'started',
                                      'timestamp': time(),
                                      'contextId': context_id }
        p.start()
        self.log.debug('Worker for processId#{0} started.'.format(process_id))
        #p.join()

    def _restart_process(self, process_id):
        if (process_id in self._workers):
            # TODO: Signal the route, maybe it wants to check for new messages?
            self.log.info('Received start signal for already running process.')
            return
        else:
            # TODO: Implement
            pass

    def do_start(self, parameter, packet):
        process_id = packet.data.get('processId')
        context_id = packet.data.get('contextId')
        self.log.info('Received message to start/restart processId#{0}'.format(process_id))
        try:
            self._start_process(process_id, context_id)
        except Exception, e:
            self.log.warn('Unable to start procesId#{0}'.format(process_id))
            self.log.exception(e)
            self.send(Packet.Reply(packet, {'status': 500, 'text': 'ERROR'}))
        else:
            self.log.info('Successfully started processId#{0}'.format(process_id))
            self.send(Packet.Reply(packet, {'status': 201, 'text': 'OK'}))

    def do_signal(self, parameter, packet):
        # TODO: Authorize signal!
        try:
            process_id = packet.data.get('processId')
            self._restart_process(process_id)
        except Exception, e:
            self.send(Packet.Reply(packet, { 'status': 500,
                                             'text': '{0}'.format(e) } ) )
        else:
            self.send(Packet.Reply(packet, { 'status': 201,
                                             'text': 'OK' } ) )

    def do_running(self, parameter, packet):
        ''' Packet indicates the process is actively working, update the timestamp '''
        process_id = packet.data.get('processId')
        if (process_id in self._workers):
            worker = self._workers.get(process_id)
            if (worker.get('timestamp') < packet.time):
                self._workers[process_id]['status'] = 'running'
                self._workers[process_id]['timestamp'] = time()

    def do_parked(self, parameter, packet):
        ''' Parking a workflow is effectively the same as shutting down.'''
        process_id = packet.data.get('processId')
        if (process_id in self._workers):
            del self._workers[process_id]
            self.log.debug('discarding parked process {0}'.format(process_id))
        return

    def do_failure(self, parameter, packet):
        ''' When a process fails shut down the worker '''
        process_id = packet.data.get('processId')
        if (process_id in self._workers):
            del self._workers[process_id]
            self.log.debug('discarding failed process {0}'.format(process_id))
        if (len(self._workers) < 10):
            self._start_a_queued_process()
        return

    def do_complete(self, parameter, packet):
        ''' When a process is complete, shut down the worker '''
        process_id = packet.data.get('processId')
        if (process_id in self._workers):
            del self._workers[process_id]
            self.log.debug('discarding completed process {0}'.format(process_id))
        self.send(Packet('coils.workflow.executor/__null',
                         'coils.workflow.archivist/deleteProcess:{0}'.format(process_id),
                         None))
        self._start_a_queued_process()

    def do_ticktock(self, parameter, packet):
        self.log.info('{0} active workers'.format(len(self._workers)))
        self._start_a_queued_process()

    def do_is_running(self, parameter, packet):
        process_id = int(parameter)
        if (process_id in self._workers):
            self.send(Packet.Reply(packet, {'status': 200, 'text': 'OK', 'running': 'YES' }))
        else:
            self.send(Packet.Reply(packet, {'status': 200, 'text': 'OK', 'running': 'NO' }))

    def do_kill(self, parameter, packet):
        process_id = int(parameter)
        signal = packet.data.get('signal', 15)
        if (process_id in self._workers):
            if (signal == 9):
                # hard kill
                # TODO: implement
                self.send(Packet.Reply(packet, {'status': 500, 'text': 'Not Implemented'}))
            elif (signal == 15):
                self.send(Packet('coils.workflow.executor/__null',
                                 'coils.workflow.process.{0}/kill:{0}'.format(process_id),
                                 None))
                self.send(Packet.Reply(packet, {'status': 201, 'text': 'OK'}))
            elif (signal == 1):
                # Reload ?
                # TODO Implement
                self.send(Packet.Reply(packet, {'status': 500, 'text': 'Not Implemented'}))
            elif (signal == 17):
                # Suspend (Park!)
                # TODO Implement
                self.send(Packet.Reply(packet, {'status': 500, 'text': 'Not Implemented'}))
            else:
                self.send(Packet.Reply(packet, {'status': 500, 'text': 'Unknown kill signal'}))
        else:
            self.send(Packet.Reply(packet, {'status': 404, 'text': 'OK', 'running': 'No worker for PID' }))
