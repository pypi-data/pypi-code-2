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
import pickle, os
from uuid             import uuid4
from time             import time, mktime
from datetime         import datetime, timedelta
from coils.foundation import *
from coils.core       import *

class TrueMatch(set):
    """This set contains the entire universe"""
    def __contains__(self, item): return True


def conv_to_set(obj):
    if isinstance(obj, (int,long)):
        return set([obj])
    if not isinstance(obj, set):
        obj = set(obj)
    return obj

def convert_from_trues(x):
    if (x is TrueMatch):
        return '*'
    return x

def convert_to_trues(x):
    if (x is None):
        return TrueMatch
    if (isinstance(x, str)):
        if (x == '*'):
            return TrueMatch
    return x

class Job(object):
    ''' Represent a job in the schedular process' database '''
    def __init__(self, route_id, data=None, run_as=0, minute=TrueMatch,
                                                        hour=TrueMatch,
                                                        day=TrueMatch,
                                                        month=TrueMatch,
                                                        days=TrueMatch):
        self.minute    = conv_to_set(minute)
        self.hour      = conv_to_set(hour)
        self.day       = conv_to_set(day)
        self.month     = conv_to_set(month)
        self.days      = conv_to_set(days)
        self.route_id  = route_id
        self.data      = data
        self.run_as    = run_as
        self.uuid      = '{{{0}}}'.format(str(uuid4()))

    def run_at(self, t):
        """Return True if this event should trigger at the specified datetime"""
        return ((t.minute    in self.minute) and
                (t.hour       in self.hour)   and
                (t.day        in self.day)    and
                (t.month      in self.month)  and
                (t.weekday()  in self.days))


class SchedularService(Service):
    __service__ = 'coils.workflow.schedular'
    __auto_dispatch__ = True
    __is_worker__     = False

    def __init__(self):
        self._ctx      = AdministrativeContext()
        self._filename = 'wf/p/schedular.pickle'
        self._delta    = timedelta(minutes=1)
        self.load_state()
        Service.__init__(self)

    def prepare(self):
        Service.prepare(self)
        self.subscribe_to_timer()

    def subscribe_to_timer(self):
        packet = Packet('{0}/__null'.format(self.__service__),
                        'coils.master/__timer_signal:subscribe',
                        None)
        self.send(packet)

    def load_state(self):
        if (os.path.exists(self._filename)):
            handle = BLOBManager.Open(self._filename, 'rb', encoding='binary')
            self._metadata = pickle.load(handle)
            BLOBManager.Close(handle)
        else:
            self._metadata = { 'schedule': [ ],
                               'upcoming': { },
                               'lasttick': None }
        self._metadata['started']    = time()
        self._metadata['reschedule'] = (time() + 1800)
        self.compute_schedule()

    def save_state(self):
        handle = BLOBManager.Open(self._filename, 'wb', encoding='binary')
        pickle.dump(self._metadata, handle)
        BLOBManager.Close(handle)

    def compute_schedule(self):
        t = datetime.now()
        upcoming =  { }
        i = 0
        while (i < 61):
            t = t + self._delta
            epoch = mktime(t.timetuple())
            for job in self._metadata['schedule']:
                if job.run_at(t):
                    if (epoch in upcoming):
                        upcoming.append(job)
                    else:
                        upcoming[epoch] = [ job ]
            i = i + 1
        self._metadata['upcoming'] = upcoming
        # Rescuedule every 30 minutes
        self._metadata['reschedule'] = (time() + 1800)

    def do_list_jobs(self, route, packet):
        run_as = packet.get('run_as', 0)
        response = { }
        for job in self._metadata['schedule']:
            if ((job.run_as == run_as) or (run_as == -1)):
                response[job.uuid] = { 'route_id':  job.route_id,
                                       'run_as':    job.run_as,
                                       'minute':    convert_from_trues(job.minute),
                                       'hour':      convert_from_trues(job.hour),
                                       'day':       convert_from_trues(job.day),
                                       'months':    convert_from_trues(job.months),
                                       'days':      convert_from_trues(job.days) }
        self.send(Packet.Reply(packet, {'status': 500, 'text': 'Not Implemented'}))

    def do_schedule_job(self, route, packet):
        job = Job(packet.data.get('route_id'),
                  packet.data.get('data', None),
                  run_as = packet.data.get('run_as', 0),
                  minute = convert_to_trues(packet.data.get('minute', None)),
                  hour   = convert_to_trues(packet.data.get('hour',   None)),
                  day    = convert_to_trues(packet.data.get('day',    None)),
                  month  = convert_to_trues(packet.data.get('months', None)),
                  days   = convert_to_trues(packet.data.get('days',   None)))
        self._metadata['schedule'].append(job)
        self.compute_schedule()
        self.save_state()
        self.subscribe_to_timer()
        self.send(Packet.Reply(packet, {'status': 201, 'uuid': job.uuid}))

    def do_unschedule_job(self, route, packet):
        self.subscribe_to_timer()
        uuid = packet.data.get('uuid')
        for job in self._metadata['schedule']:
            if (job.uuid == uuid):
                self._metadata['schedule'].remove(job)
                break
        else:
            self.send(Packet.Reply(packet, {'status': 404, 'text': 'Job {0} not found'.format(uuid)}))
            return
        self.compute_schedule()
        self.save_state()
        self.send(Packet.Reply(packet, {'status': 201, 'text': 'Job {0} cancelled.'.format(uuid)}))

    def do___timer(self, parameter, packet):
        now = time()
        timestamps = self._metadata.get('upcoming').keys()
        for stamp in timestamps:
            if (stamp < now):
                for job in self._metadata.get('upcoming').get(stamp):
                    process = self._ctx.run_command('process::new', values={'route_id': job.route_id,
                                                                            'data':     job.data})
                    self._ctx.run_command('process::start', process=process, runas=job.run_as)
                del self._metadata['upcoming'][stamp]
        if (self._metadata['reschedule'] < now):
            self.compute_schedule()
        return
