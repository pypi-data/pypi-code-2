# Copyright (C) 2010, 2011 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of lava-dev-tool
#
# lava-dev-tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# lava-dev-tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lava-dev-tool.  If not, see <http://www.gnu.org/licenses/>.


from Queue import Queue
from threading import Thread
import subprocess
try:
    import posix
except ImportError:
    posix = None


class ExternalCommand(object):

    def _popen(self, *args, **kwargs):
        if posix:
            kwargs['close_fds'] = True
        return subprocess.Popen(*args, **kwargs)

    def run(self, *args, **kwargs):
        proc = self._popen(*args, **kwargs)
        proc.communicate()
        return proc.returncode

    def run_checked(self, *args, **kwargs):
        returncode = self.run(*args, **kwargs)
        if returncode != 0:
            raise subprocess.CalledProcessError(
                returncode, kwargs.get("args") or args[0])


class ExternalCommandWithDelegate(ExternalCommand):

    def __init__(self, display_delegate):
        self._queue = Queue()
        self._display_delegate = display_delegate

    def _read_stream(self, stream, marker):
        for line in iter(stream.readline, ''):
            self._queue.put((marker, line)) 

    def _drain_queue(self):
        while True:
            args = self._queue.get()
            if args is None:
                break
            self._display_delegate.display_subprocess_output(*args)

    def run(self, *args, **kwags):
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.PIPE
        proc = self._popen(*args, **kwargs)

        stdout_reader = Thread(
            target=self._read_stream, 
            args=(proc.stdout, "stdout"))
        stderr_reader = Thread(
            target=self._read_stream,
            args=(proc.stderr, "stderr"))
        ui_printer = Thread(target=self._drain_queue)

        stdout_reader.start()
        stderr_reader.start()
        ui_printer.start()
        try:
            proc.communicate()
        finally:
            self._queue.put(None)
            stdout_reader.join()
            stderr_reader.join()
            ui_printer.join()
        return proc.returncode
