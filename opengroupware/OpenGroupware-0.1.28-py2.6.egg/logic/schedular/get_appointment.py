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
from sqlalchemy         import *
from coils.core         import *
from coils.core.logic   import GetCommand
from coils.foundation   import Appointment, Contact

class GetAppointment(GetCommand):
    __domain__ = "appointment"
    __operation__ = "get"

    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)
        self._caldav_uid = None
        if (bool(params.get('visible_only', False))):
            self._required_right = 'v'
        else:
            self._required_right = 'l'
        if (len(self.object_ids) == 0):
            if ('uid' in params):
                self._caldav_uid = unicode(params.get('uid'))
                self.mode = RETRIEVAL_MODE_SINGLE

    def add_comments(self, data):
        for appointment in data:
            comment = self._ctx.run_command('appointment::get-comment-text', appointment=appointment, access_check=False)
            if (comment is not None):
                self.log.debug('retrieved and set comment on appointment id#{0}'.format(appointment.object_id))
                appointment.set_comment(comment)
        return data

    def run(self, **params):
        db = self._ctx.db_session()
        #print self.object_ids
        if (self._caldav_uid is None):
            query = db.query(Appointment).filter(and_(Appointment.object_id.in_(self.object_ids),
                                                       Appointment.status != 'archived'))
        else:
            #query = db.query(Appointment).filter(Appointment.status != 'archived')
            #query = query.join(ObjectProperty).filter(and_(ObjectProperty.name == 'caldav_uid',
            #                                                ObjectProperty.namespace == 'www.opengroupware.us',
            #                                                ObjectProperty._string_value == self._caldav_uid))
            query = db.query(Appointment).filter(and_(Appointment.status != 'archived',
                                                       Appointment.caldav_uid == self._caldav_uid))
        self.set_return_value(self.add_comments(query.all()), right=self._required_right)
