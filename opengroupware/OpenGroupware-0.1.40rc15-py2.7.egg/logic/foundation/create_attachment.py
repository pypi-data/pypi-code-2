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
#
import shutil
from sqlalchemy          import *
from coils.core          import *
from keymap              import COILS_ATTACHMENT_KEYMAP
from command             import AttachmentCommand

class CreateAttachment(Command, AttachmentCommand):
    __domain__ = "attachment"
    __operation__ = "new"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self.values = {}
        self.values['mimetype'] = params.get('mimetype', 'application/octet-stream')
        self.values['context_id'] = params.get('context_id', self._ctx.account_id)
        if ('entity' in params):
            self.values['related_id'] = params.get('entity').object_id
        else:
            self.values['related_id'] = params.get('related_id', None)
        self.values['kind'] = params.get('kind', None)
        self.values['expiration'] = params.get('expiration', None)
        self.values['webdav_uid'] = params.get('name', None)
        if ('data' in params):
            self.handle = None
            self.data = params['data']
        elif ('filename' in params):
            self.handle = open(params['filename'], 'rb')
        elif ('handle' in params):
            self.handle = params['handle']
        else:
            raise CoilsException('No attachment data or source specified')

    def run(self):
        db = self._ctx.db_session()
        attachment = Attachment()
        attachment.take_values(self.values, COILS_ATTACHMENT_KEYMAP)
        setattr(attachment, 'created',  self._ctx.get_utctime())
        setattr(attachment, 'uuid', self.generate_attachment_id())
        try:
            attachment_file = BLOBManager.Open(self.attachment_text_path(attachment), 'w', encoding='binary', create=True)
            if (self.handle is None):
                if (self.data is not None):
                    attachment_file.write(self.data)
            else:
                self.handle.seek(0)
                shutil.copyfileobj(self.handle, attachment_file)
            setattr(attachment, 'size', attachment_file.tell())
            BLOBManager.Close(attachment_file)
        except Exception, e:
            self.log.exception(e)
            print e
            raise CoilsException('Failure to allocate attachment contents')
        self._ctx.db_session().add(attachment)
        self._result = attachment
