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
from coils.foundation   import *
from coils.core         import *
from coils.core.logic   import CreateCommand
from keymap             import COILS_APPOINTMENT_KEYMAP

class CreateAppointment(CreateCommand):
    __domain__    = "appointment"
    __operation__ = "new"

    def prepare(self, ctx, **params):
        self.keymap = COILS_APPOINTMENT_KEYMAP
        self.entity = Appointment
        CreateCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        CreateCommand.parse_parameters(self, **params)

    def do_participants(self):
        participants = KVC.subvalues_for_key(self.values, ['_PARTICIPANTS', 'participants'])
        if (len(participants) == 0):
            participants = [ { 'companyId': self._ctx.account_id } ]
        self._ctx.run_command('appointment::set-participants', participants=participants,
                                                               appointment=self.obj)

    def create_resource_string(self):
        if ('_RESOURCES' in self.values):
            resources = [ ]
            for entity in self.values.get('_RESOURCES'):
                if ('objectId' in entity):
                    resources.append(int(entity.get('objectId')))
            names = self._ctx.run_command('resource::get-names', ids=resources)
            self.obj.set_resource_names(names)

    def set_comment_text(self):
        self.obj.set_comment(self._ctx.run_command('appointment::set-comment-text', appointment=self.obj,
                                                                   text=self.values.get('comment', '')))

    def run(self):
        CreateCommand.run(self)
        self.create_resource_string()
        self.do_participants()
        self.set_comment_text()
        self.save()
