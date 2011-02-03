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
from keymap             import COILS_DOCUMENT_KEYMAP

class CreateDocument(CreateCommand):
    __domain__    = "document"
    __operation__ = "new"

    def prepare(self, ctx, **params):
        self.keymap = COILS_DOCUMENT_KEYMAP
        self.entity = Document
        CreateCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        CreateCommand.parse_parameters(self, **params)
        self._folder      = params.get('folder', None)
        self._project     = params.get('project', None)
        self._appointment = params.get('appointment', None)
        self._company     = params.get('contact', params.get('enterprise', None))
        self._name        = params.get('name', None)

    def run(self):
        CreateCommand.run(self)
        self.obj.extension    = self._name.split('.')[-1]
        self.obj.name         = '.'.join(self._name.split('.')[:-1])
        self.obj.creator_id   = self._ctx.account_id
        self.obj.created  = datetime.now()
        self.obj.modified = self.obj.created
        if (self._folder is not None): self.obj.folder_id = self._folder.object_id
        if (self._project is not None): self.obj.project_id = self._project.object_id
        if (self._company is not None): self.obj.company_id = self._company.object_id
        if (self._appointment is not None): self.obj.appointment_id = self._appointment.object_id
        self.save()
        self._result = self.obj
