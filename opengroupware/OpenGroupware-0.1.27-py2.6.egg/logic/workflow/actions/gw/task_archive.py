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
# THE SOFTWARE.
#
import os
from pytz                import timezone
from datetime            import datetime, timedelta
from coils.core          import *
from coils.core.logic    import ActionCommand
from coils.core.xml      import Render as XML_Render

class ArchiveTaskAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "archive-task"
    __aliases__   = [ 'archiveTask', "archiveTaskAction" ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        task = self._ctx.run_command('task::comment',
                                     values={ 'action': 'archive',
                                             'comment': self._comment},
                                     id=self._task_id)
        results = XML_Render.render(task, self._ctx)
        self._wfile.write(results)
        self._wfile.flush()

    def parse_action_parameters(self):
        self._comment = self._params.get('comment', None)
        self._task_id = self._params.get('taskId', self._process.task_id)
        if (self._task_id is None):
            raise CoilsException('Attempt to archive task, but no task available.')
