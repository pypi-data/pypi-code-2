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
from datetime         import datetime, timedelta
from pytz             import timezone
from sqlalchemy       import *
from coils.core       import *

RETRIEVAL_MODE_SINGLE   = 1
RETRIEVAL_MODE_MULTIPLE = 2

class GetCommand(Command):

    def __init__(self):
        Command.__init__(self)
        self.query_by = None

    def set_multiple_result_mode(self):
        self.mode = RETRIEVAL_MODE_MULTIPLE

    def set_single_result_mode(self):
        self.mode = RETRIEVAL_MODE_SINGLE

    @property
    def single_result_mode(self):
        if (self.mode == RETRIEVAL_MODE_SINGLE):
            return True
        return False

    @property
    def multiple_result_mode(self):
        if (self.mode == RETRIEVAL_MODE_MULTIPLE):
            return True
        return False

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self.object_ids = []
        if (('id' in params) or ('ids' in params)):
            self.query_by = 'object_id'
            if ('id' in params):
                self.set_single_result_mode()
                self.object_ids.append(int(params['id']))
            elif ('ids' in params):
                self.set_multiple_result_mode()
                for object_id in params['ids']:
                    self.object_ids.append(int(object_id))

    def set_return_value(self, data, right='r'):
        if (isinstance(data, list)):
            if ((self.access_check) and (self._ctx.account_id > 10000)):
                c = len(data)
                data = self._ctx.access_manager.filter_by_access(self._ctx, right, data)
                c = c - len(data)
                self.log.debug('access manager filtered out {0} objects.'.format(c))
            else:
                self.log.debug('access processing disabled!')
            if (self.single_result_mode):
                if (len(data) > 0):
                    self._result = data[0]
                else:
                    self._result = None
            elif (self.multiple_result_mode):
                    self._result = data
            else:
                raise CoilsException('Unknown mode value')
            return
        raise CoilsException('Data for Get result is not a list')
        self._result = None