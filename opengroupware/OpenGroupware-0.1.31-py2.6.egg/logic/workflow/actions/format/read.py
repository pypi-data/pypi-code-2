#
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
#
import os
from coils.core          import *
from coils.core.logic    import ActionCommand

class ReadAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "read"
    __aliases__   = [ 'readAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        format = self._ctx.run_command('format::get', name=self._format)
        format.process_in(self._rfile, self._wfile)
        self._wfile.flush()
        if (self._reject_label is not None):
            self.log.debug('Storing rejected records in message labeled {0}'.format(self._reject_label))
            self.store_in_message(self._reject_label, format.reject_buffer)

    def parse_action_parameters(self):
        self._format = self._params.get('format', 'StandardRaw')
        self._reject_label = self._params.get('rejectionsLabel', None)
