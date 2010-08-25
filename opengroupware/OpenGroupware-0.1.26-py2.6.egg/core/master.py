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
# THE SOFTWARE.

import logging, sys, multiprocessing, datetime, Queue, time, pprint, os
from service       import Service

class MasterService(Service):
    __service__ = 'coils.master'
    __auto_dispatch__ = True
    __is_worker__     = False

    def __init__(self):
        Service.__init__(self)
        self._workers = { }

    def prepare(self):
        try:
            import procname
            procname.setprocname('service::{0}'.format(self.__service__))
        except:
            self.log.info('Failed to set process name for service')

    def start(self):
        log = logging.getLogger('bootstrap')
        for name in self.service_list:
            try:
                service = self.get_service(name)
                p = multiprocessing.Process(target=service.run, args=())
                self.append_process(name, p)
                self.get_process(name).start()
            except Exception, e:
                log.warn('Failed to start service {0}'.format(name))
                log.exception(e)
            else:
                log.info('Started service {0} as PID#{1}'.format(name, self.get_process(name).pid))
        log.info('All services started.')

    @property
    def service_list(self):
        return self._workers.keys()

    def append_service(self, name, target):
        self._workers[name] = [ target ]

    def append_process(self, name, process):
        self._workers[name].append(process)

    def get_service(self, name):
        return self._workers[name][0]

    def get_process(self, name):
        return self._workers[name][1]
