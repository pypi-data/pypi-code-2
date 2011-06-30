#
# Copyright (c) 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core           import *
from coils.net            import PathObject

class EntityObject(PathObject):

    def __init__(self, parent, name, **params):
        self.name = name
        PathObject.__init__(self, parent, **params)

    def do_PUT(self, name):
        payload = self.request.get_request_payload()
        mimetype = self.request.headers.get('Content-Type', 'application/octet-stream')
        scratch_file = BLOBManager.ScratchFile()
        scratch_file.write(payload)
        scratch_file.seek(0)
        attachment = None
        attachment = self.context.run_command('attachment::new', handle=scratch_file,
                                                                 name=name,
                                                                 entity=self.entity,
                                                                 mimetype=mimetype)
        self.context.commit()
        if (attachment is not None):
            self.request.simple_response(201,
                                         mimetype=mimetype,
                                         headers= { 'Content-Length': str(attachment.size),
                                                    'Etag': attachment.uuid,
                                                    'Content-Type': attachment.mimetype } )
        else:
            # TODO; Can this happen without an exception having occurred?
            raise CoilsExcpetion('Ooops!')
