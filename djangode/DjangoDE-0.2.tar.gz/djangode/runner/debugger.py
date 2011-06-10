# DjangoDE, an integrated development environment for Django
# Copyright (C) 2010-2011 Andrew Wilkinson
#
# This program is free software; you can redistribute it and/or
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from bdb import Bdb
import threading

from djangode.runner.send_msg import send_msg

debug_lock = threading.Event()

class Debugger(Bdb):
    instance = None

    def user_line(self, frame):
        if self.break_here(frame):
            local_vars = []
            for (var_name, var_value) in frame.f_locals.items():
                local_vars.append((var_name, repr(var_value)))
            send_msg("debug", frame.f_code.co_filename, frame.f_lineno, local_vars)

            debug_lock.wait()
            debug_lock.clear()

        return Bdb.user_line(self, frame)

def continue_running():
    debug_lock.set()

    return "done"

def set_breakpoints(break_list):
    Debugger.instance.clear_all_breaks()

    for (filename, line_no) in break_list:
        Debugger.instance.set_break(filename, line_no)
