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
from sqlalchemy       import *
from sqlalchemy.orm   import *
from coils.core       import *
from process          import Process as WFProcess
import multiprocessing

class QueueManagerService(Service):
    __service__ = 'coils.workflow.queueManager'
    __auto_dispatch__ = True
    __is_worker__     = True
    __TimeOut__       = 60

    def __init__(self):
        Service.__init__(self)

    def prepare(self):
        Service.prepare(self)
        self._slots  = 0
        self._enabled  = True
        self._do_start = False
        self._ctx = AdministrativeContext({}, broker=self._broker)

    def work(self):
        if (self._enabled):
            if (self._do_start):
                self._start_queued_processes()

    def _request_process_start(self, pid, cid):
        self.send(Packet('coils.workflow.queueManager/__null',
                         'coils.workflow.executor/start',
                         { 'processId': pid,
                           'contextId': cid } ))

    def _get_worker_threshold(self):
        return 10

    def do_checkqueue(self, parameter, packet):
        if (parameter is None):
            workers = 9
        else:
            workers = int(parameter)
        self._slots = self._get_worker_threshold() - workers
        self.log.info('Determined {0} worker slots are available.'.format(self._slots))
        if (self._slots > 0):
            self._do_start = True
        else:
            self._do_start = False
        self.send(Packet.Reply(packet, {'status': 201, 'text': 'OK'}))
        return

    def do_enable(self, parameter, packet):
        self._enabled = True
        return

    def do_disabled(self, parameter, packet):
        self._enabled = False
        return

    def do_reaper_scan(self):
        self._scan_running_processes()
        self.send(Packet.Reply(packet, {'status': 201, 'text': 'OK'}))

    def do_reap(self, parameter, packet):
        process_id = int(parameter)
        if (packet.data.get('running') == 'YES'):
            # executor says it has a worker for this PID, do NOT reap
            return


    def _start_queued_processes(self):
        self.log.info('Checking for queued processes')
        self._do_start = False
        if self._slots < 1:
            self.log.info('No available worker slots expected, not requesting.')
            return
        db = self._ctx.db_session()
        try:
            for pid, cid in db.query(Process.object_id, Process.owner_id).\
                                filter(and_(Process.state=='Q',
                                             Process.priority > 0)).\
                                order_by(Process.priority.desc()).\
                                limit(self._slots).all():
                self.log.info('Requesting start of queued processId#{0}'.format(pid))
                self._request_process_start(pid, cid)
        except Exception, e:
            self.log.exception(e)
        self.log.info('Checking for queued complete')
        self._ctx.commit()
        self.log.info('Committed.')

    def _scan_running_processes(self):
        db = self._ctx.db_session()
        running_pids = db.query(Process.object_id).filter(Process.state=='R').all()
        if (len(running_pids) > 0):
            for pid in running_pids:
                self.send(Packet('coils.workflow.queueManager/reap:{0}'.format(pid),
                                 'coils.workflow.executor/is_running:{0}'.format(pid),
                                 None))
