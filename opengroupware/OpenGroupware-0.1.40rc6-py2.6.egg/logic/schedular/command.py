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
from copy import deepcopy
import datetime, pytz, re


class AppointmentCommand(object):

    def set_ics_properties(self):
        flags    = self.values.get('FLAGS', [])
        timezone = pytz(self.obj.timezone)
        self._ctx.set_property(self.obj, 'http://www.opengroupware.us/ics', 'timezone', self.obj.timezone)
        if ('ALLDAY' in  flags):
            self._ctx.set_property(self.obj, 'http://www.opengroupware.us/ics', 'isAllDay', 'YES')
            self._ctx.set_property(self.obj, 'http://www.opengroupware.us/ics', 'allDayStart', 'YES')
            self._ctx.set_property(self.obj, 'http://www.opengroupware.us/ics', 'allDayEnd', 'YES')
        else:
            self._ctx.set_property(self.obj, 'http://www.opengroupware.us/ics', 'isAllDay', 'NO')
            if(timezone.dst(self.obj.start)):
                self._ctx.set_property(self.obj, 'http://www.opengroupware.us/ics', 'isStartDST', 'YES')
            else:
                self._ctx.set_property(self.obj, 'http://www.opengroupware.us/ics', 'isStartDST', 'NO')
            if(timezone.dst(self.obj.end)):
                self._ctx.set_property(self.obj, 'http://www.opengroupware.us/ics', 'isEndDST', 'YES')
            else:
                self._ctx.set_property(self.obj, 'http://www.opengroupware.us/ics', 'isEndDST', 'NO')
