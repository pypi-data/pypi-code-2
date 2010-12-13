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
import shutil
from coils.foundation   import *
from coils.core         import *
from coils.core.logic   import CreateCommand

class CreateVersion(CreateCommand):
    __domain__    = "document"
    __operation__ = "new-version"

    def prepare(self, ctx, **params):
        self.keymap = { }
        self.entity = DocumentVersion
        CreateCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        if ('document' in params):
            self._document = params.get('document')
        else:
            raise CoilsException('Request to create a version with no document.')
        self._rfile  = params.get('handle', None)
        self._project = params.get('project', None)

    def run(self):
        self.obj = DocumentVersion(self._document)
        self.set_object_id()
        self.set_owner()
        if (self._project is not None):
            # Project document
            ds = blob_manager_for_ds(self._project)
            self._document.version_count += 1
            self.obj.version = self._document.version_count
            path = ds.create_path(self._document, self.obj)
            if (path is None):
                raise CoilsException('Data source {0} provided no path for BLOB (objectId={1}, version={2})'.\
                    format(ds, self._document.object_id, self._document.version))
        else:
            raise NotImplementedException('Non-project documents not yet supported')
        self.log.debug('Creating new version @ {0}/{1}'.format(path[0], path[1]))
        wfile = BLOBManager.Create(path, encoding='binary')
        if (wfile is None):
            raise CoilsException('Unable to open path {0}/{1} to create version'.\
                format(path[0], path[1]))
        shutil.copyfileobj(self._rfile, wfile)
        wfile.flush()
        self.obj.file_size = BLOBManager.SizeOf(path)
        self._document.file_size = self.obj.file_size
        self.save()
        self._result = self.obj
        # TODO: file_size
        # TODO: is_not
        # TODO: is_object_link
        # TODO: is_index_doc
        # TODO: db_status

