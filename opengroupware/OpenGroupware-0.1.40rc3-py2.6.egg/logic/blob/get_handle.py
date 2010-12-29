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
from sqlalchemy import *
from coils.core import *
from coils.core.logic import GetCommand


class GetDocumentHandle(GetCommand):
    __domain__ = "document"
    __operation__ = "get-handle"

    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)
        self._mode = params.get('mode', 'rb')
        self._encoding = params.get('encoding', 'binary')

    def run(self, **params):
        filename = None
        db = self._ctx.db_session()
        document = self._ctx.run_command('document::get', id=self.object_ids[0])
        if (document is not None):
            if (document.project_id is not None):
                # TODO: We have to use the project type to determine the correct
                # mechanism for constructing the path to the BLOB; for now we are
                # assuming a SKYfs [DB} project.
                project = self._ctx.run_command('project::get', id = document.project_id)
                if (project is not None):
                    manager = blob_manager_for_ds(project)
                    path = manager.get_path(document)
                    if (path is not None):
                        self._result = BLOBManager.Open(path, self._mode, self._encoding)
                    else:
                        raise CoilsException('Unable to determine path to document.')
                else:
                    raise CoilsException('Unable discover document\'s project (container).')
            else:
                # TODO: Implement!  How do we locate non-project documents???
                raise NotImplementedException('Non-project documents not yet supported')
        else:
            raise CoilsException('Unable discover specified document.')


class GetNoteHandle(GetCommand):
    # TODO: This doesn't use the BLOB manager!
    __domain__ = "note"
    __operation__ = "get-handle"

    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)
        self._mode = params.get('mode', 'rb')
        self._encoding = params.get('encoding', 'binary')

    def run(self, **params):
        filename = None
        db = self._ctx.db_session()
        query = db.query(Note).filter(Note.object_id.in_(self.object_ids))
        note = query.first()
        handle = BLOBManager.Open(note.get_path(), self._mode)
        if (handle is not None):
            self._result = handle
            return
        # Send admin-notice recarding invalid path
        message = 'Note path "{0}" is invalid (Note objectId#{1}).'.format(note.get_path(), note.object_id)
        if (self._ctx.amq_available):
            self._ctx.send_administrative_notice(
                category='data',
                urgency=6,
                subject='Path to Note with objectId#{0} is invalid'.format(note.object_id),
                message=message)
        # raise exception
        raise CoilsException(message)
