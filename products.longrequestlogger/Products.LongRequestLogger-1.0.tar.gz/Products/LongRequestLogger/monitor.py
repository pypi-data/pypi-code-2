##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Leonardo Rochael Almeida <leonardo@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from threading import Thread
from threading import Condition
from Products.LongRequestLogger import dumper

class Monitor(Thread):
    """Logs the stack-trace of a thread until it's stopped

    m = Monitor(thread.get_ident(), timeout=5, interval=2)

    Wait 5 seconds before dumping the stack-trace of the identified thread
    every 2 seconds.

    m.stop()
    
    Stop the monitoring, whether timed-out or not
    """

    running = False

    def __init__(self,
                 thread_id=None,
                 timeout=None,
                 interval=None):
        Thread.__init__(self)
        self.dumper = dumper.Dumper(thread_id=thread_id)
        self.timeout = timeout or self.dumper.timeout
        self.interval = interval or self.dumper.interval
        self.running_condition = Condition()
        if self.dumper.is_enabled():
            self.running = True
            self.start()

    def stop(self):
        """Stop monitoring the other thread"""
        # this function is called by the other thread, when it wants to stop
        # being monitored
        self.running_condition.acquire()
        try:
            if not self.running:
                return # yes, the finally clause will be run, don't worry
            self.running = False
            self.running_condition.notify()
        finally:
            self.running_condition.release()
        self.join()

    def run(self):
        self.running_condition.acquire()
        self.running_condition.wait(self.timeout)
        # If the other thread is still running by now, it's time to monitor it
        try:
            while self.running:
                self.dumper()
                self.running_condition.wait(self.interval)
        finally:
            self.running_condition.release()
