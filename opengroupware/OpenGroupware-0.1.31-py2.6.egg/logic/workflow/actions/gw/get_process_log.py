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
from coils.core          import *
from coils.core.logic    import ActionCommand

# TODO: Support retrieval of the log as XML
class GetProcessLogAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "get-process-log"
    __aliases__   = [ 'getProcessLogAction', 'getProcessLog' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def _callback(self, uuid, source, target, data):
        self._wfile.write(data.get('payload'))
        return True

    def do_action(self):
        self._ctx.run_command('process::get-log', id=self._id,
                                                  format=self._format,
                                                  callback=self._callback)
        if(self._ctx.wait()):
            # TODO: Unable to retrieve process-log, what should we do?
            pass

    def result_mimetype(self):
        return 'text/plain'

    def parse_action_parameters(self):
        self._id     = int(self._params.get('processId', self._process.object_id))
        self._format = self._params.get('format', 'text/plain')
        #TODO: Support label substitutions - the value must be text
        #self._id = self.process_label_substitutions(self._id)

    def do_epilogue(self):
        pass
