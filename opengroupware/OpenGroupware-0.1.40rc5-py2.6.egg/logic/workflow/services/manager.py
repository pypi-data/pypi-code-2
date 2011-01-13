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

class ManagerService(Service):
    __service__ = 'coils.workflow.manager'
    __auto_dispatch__ = True
    __is_worker__     = True
    __TimeOut__       = 60

    def __init__(self):
        Service.__init__(self)

    def prepare(self):
        Service.prepare(self)
        self._enabled  = True
        self._ctx = AdministrativeContext({}, broker=self._broker)
        self._last_time = time()

    def work(self):
        if (self._enabled):
            if ((time() - self._last_time) > 360):
                self._start_queued_processes()
                self._last_time = time()

    def _request_process_start(self, pid):
        self.send(Packet('coils.workflow.manager/__null',
                         'coils.workflow.executor/start',
                         { 'processId': pid } ))

    def _get_worker_threshold(self):
        return 10

    def do_checkqueue(self, parameter, packet):
        self._start_queued_processes()
        self.send(Packet.Reply(packet, {'status': 201, 'text': 'OK'}))
        return

    def do_enable(self, parameter, packet):
        self._enabled = True
        return

    def do_failed(self, parameter, packet):
        process_id = int(parameter)
        process = self._ctx.run_command('process::get', id=process_id)
        if (process is None):
            self.log.warn('Request to fail processId#{0} but process could not be found.'.format(process_id))
            self.send(Packet.Reply(packet, { 'status': 404, 'text': 'No such process' } ) )
        else:
            if (process.state == 'R'):
                self.log.warn('Marking running processId#{0} as failed.'.format(process_id))
                self.send_administrative_notice(
                        category='workflow',
                        urgency=4,
                        subject='Defunct OIE Worker Detected',
                        message='Detected processId#{0} in defunct state, process will be failed.'.format(process_id))
                process.state = 'F'
                self._ctx.commit()
                self.send(Packet(None,
                                 'coils.workflow.logger/log',
                                 { 'process_id': process_id,
                                   'message': 'Manager set state of process to failed.' } ) )
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

    def do_queue(self, parameter, packet):
        process_id = int(parameter)
        self.send(Packet(None,
                         'coils.workflow.logger/log',
                         { 'process_id': process_id,
                           'message': 'Request to place in queued state.'}))
        process = self._ctx.run_command('process::get', id=process_id)
        if (process is None):
            self.log.warn('Request to queue processId#{0} but process could not be found.'.format(process_id))
            self.send(Packet.Reply(packet, { 'status': 404, 'text': 'No such process' } ) )
        else:
            if (process.state in ('I', 'H')):
                process.state = 'Q'
                self._ctx.commit()
                self.send(Packet.Reply(packet, { 'status': 201, 'text': 'OK' } ) )
            elif (process.state == 'Q'):
                self.send(Packet(None,
                                 'coils.workflow.logger/log',
                                 { 'process_id': process_id,
                                   'message': 'Process is already in queued state' } ) )
                self.send(Packet.Reply(packet, { 'status': 201,
                                                 'text': 'OK, No action.' } ) )
            else:
                self._ctx.rollback()
                message = 'Process cannot be queued from state {0}'.format(process.state)
                self.send(Packet(None,
                                 'coils.workflow.logger/log',
                                 { 'process_id': process_id,
                                   'message': message } ) )
                self.send(Packet.Reply(packet, { 'status': 403, 'text': message } ) )

    def do_get_properties(self, parameter, packet):
        process_id = int(parameter)
        self.send(Packet(None,
                         'coils.workflow.logger/log',
                         { 'process_id': process_id,
                           'message': 'Reqeust for OIE properties'}))
        props = { }
        route = None
        process = self._ctx.run_command('process::get', id=process_id)
        if (process is not None):
            if (process.route_id is not None):
                route = self._ctx.run_command('route::get', id=process.route_id)
            # WARN: The process may have been created, but not started, and then the route
            # subsequently deleted - so it is not impossible to have a process with a
            # route_id that cannot be loaded *BUT* this means that the process will NOT
            # have the properties that would have otherwise been 'inherited' via translucence.
            # This is clearly administrative *GOTCHA*.
            if (route is not None):
                # Load the OIE properties from the route
                route_group = str(route.object_id)
                route_id    = int(route.object_id)
                for prop in self._ctx.property_manager.get_properties(route):
                    if prop.namespace == 'http://www.opengroupware.us/oie':
                        if (prop.name.lower() == 'routegroup'):
                            route_group = str(prop.get_value())
                        else:
                            self.log.debug('Route OIE property {0} = {1}'.format(prop.name, prop.get_value()))
                        props[prop.name] = prop.get_value()
            else:
                # Ad-hoc processes use the processId as the routeId and routeGroup
                route_group = str(process.object_id)
                route_id    = str(process.object_id)
            # Now load OIE properties from process, which may overwrite those inherited
            # from the route.
            for prop in self._ctx.property_manager.get_properties(process):
                if prop.namespace == 'http://www.opengroupware.us/oie':
                    if (prop.name.lower() == 'routegroup'):
                        route_group = str(prop.get_value())
                    else:
                        self.log.debug('Process OIE property {0} = {1}'.format(prop.name, prop.get_value()))
                        props[prop.name] = prop.get_value()
            self.send(Packet.Reply(packet, {'status':      201,
                                            'text':        'OK',
                                            'properties':  props,
                                            'process_id':  process_id,
                                            'context_id':  process.owner_id,
                                            'route_id':    route_id,
                                            'route_group': route_group}))
        else:
            self.send(Packet.Reply(packet, {'status': 404,
                                            'text': 'No such process as {0}'.format(process_id)}))

    def _start_queued_processes(self):
        self.log.info('Checking for queued processes')
        db = self._ctx.db_session()
        try:
            for pid, cid in db.query(Process.object_id, Process.owner_id).\
                                filter(and_(Process.state=='Q',
                                             Process.priority > 0)).\
                                order_by(Process.priority.desc()).\
                                limit(10).all():
                self.send(Packet(None,
                                 'coils.workflow.logger/log',
                                 { 'process_id': pid,
                                   'message': 'Reqeusting start from queued state'}))
                self._request_process_start(pid)
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
                self.send(Packet('coils.workflow.manager/reap:{0}'.format(pid),
                                 'coils.workflow.executor/is_running:{0}'.format(pid),
                                 None))
