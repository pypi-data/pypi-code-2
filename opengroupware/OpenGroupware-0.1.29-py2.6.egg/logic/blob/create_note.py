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
from datetime           import datetime
from coils.foundation   import *
from coils.core         import *
from coils.core.logic   import CreateCommand
from keymap             import COILS_NOTE_KEYMAP

class CreateNote(CreateCommand):
    __domain__    = "note"
    __operation__ = "new"

    def prepare(self, ctx, **params):
        self.keymap = COILS_NOTE_KEYMAP
        self.entity = Note
        CreateCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        CreateCommand.parse_parameters(self, **params)
        if ('text' in params):
            self.values['text'] = params['text']
        if ('context' in params):
            self._context = params.get('context')

    def run(self):
        CreateCommand.run(self)
        if (isinstance(self._context, Appointment)):
            self.obj.appointment_id = self._context.object_id
        elif (isinstance(self._context, Project)):
            self.obj.project_id = self._context.object_id
        elif (isinstance(self._context, Contact)):
            self.obj.company_id = self._context.object_id
        elif (isinstance(self._context, Enterprise)):
            self.obj.company_id = self._context.object_id
        self.obj.created = datetime.now()
        self.obj.modified = self.obj.created
        #self.obj.set_text(Backend.store_root(), self.values.get('text', ''))
        self.save()
