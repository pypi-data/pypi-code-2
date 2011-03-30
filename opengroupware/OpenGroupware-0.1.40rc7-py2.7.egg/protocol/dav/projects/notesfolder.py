# Copyright (c) 2010 Tauno Williams <awilliam@whitemice.org>
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
import urllib
from coils.protocol.dav.foundation     import DAVFolder
from noteobject                        import NoteObject

class NotesFolder(DAVFolder):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)

    def supports_PUT(self):
        return True

    def _load_contents(self):
        notes = self.context.run_command('project::get-notes', id=self.entity.object_id)
        for note in notes:
            self.insert_child(note.title, note)
        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if  (self.load_contents()):
            if (self.has_child(name)):
                return NoteObject(self, name, entity=self.get_child(name),
                                               request=self.request,
                                               context=self.context)
        self.no_such_path()

    def do_PUT(self, request_name):
        # TODO: Support If-Match header!
        if (self.load_contents()):
            self.log.debug('Requested label is {0}.'.format(request_name))
            payload = self.request.get_request_payload()
            if (self.has_child(request_name)):
                # update
                self.context.run_command('note::set', object=self.get_child(request_name),
                                                      text=payload)
            else:
                # create
                self.context.run_command('note::new', values={'title': request_name,
                                                              'projectId': self.entity.object_id },
                                                      text=payload)
            self.context.commit()
        self.request.send_response(201, 'OK')
        self.request.send_header('etag', self.get_property_GETETAG())
        self.request.send_header('Location', '{0}/{1}'.format(self.get_path(), request_name))
        self.request.send_header('Content-Type', 'text/plain')
        self.request.send_header('Content-Length', str(note.size))
        self.request.end_headers()
        #w.flush()