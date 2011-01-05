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
from time          import strftime, gmtime, time
from coils.core    import *
from coils.net     import DAVObject

class DocumentObject(DAVObject):
    _MIME_MAP_ = None

    def __init__(self, parent, name, **params):
        DAVObject.__init__(self, parent, name, **params)
        if (DocumentObject._MIME_MAP_ is None):
            sd = ServerDefaultsManager()
            DocumentObject._MIME_MAP_ = sd.default_as_dict('CoilsExtensionMIMEMap')

    def _get_mimetype(self):
        if (self.entity.extension is not None):
            kind = self.entity.extension.lower()
            if (kind in DocumentObject._MIME_MAP_):
                return DocumentObject._MIME_MAP_[kind]
        return 'application/octet-stream'

    def get_property_webdav_getlastmodified(self):
        x = gmtime(time())
        return strftime("%a, %d %b %Y %H:%M:%S GMT", x)

    def get_property_webdav_getcontentlength(self):
        return str(self.entity.file_size)

    def get_property_webdav_creationdate(self):
        if (self.entity.created is not None):
            return self.entity.created.strftime('%a, %d %b %Y %H:%M:%S GMT')
        else:
            return self.get_property_webdav_getlastmodified()

    def get_property_webdav_getlastmodified(self):
        if (self.entity.modified is not None):
            return self.entity.modified.strftime('%a, %d %b %Y %H:%M:%S GMT')
        else:
            return strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime(time()))

    def get_property_webdav_getcontenttype(self):
        return self._get_mimetype()

    def do_HEAD(self):
        self.request.simple_response(201,
                                     data=None,
                                     mimetype=self.entity.get_mimetype(),
                                     headers={ 'etag': self.get_property_GETETAG(),
                                               'Content-Length': str(self.entity.file_size) } )

    def do_GET(self):
        handle = self.context.run_command('document::get-handle', id=self.entity.object_id)
        self.request.stream_response(200,
                                     stream=handle,
                                     mimetype=self.entity.get_mimetype(),
                                     headers={ 'etag': self.get_property_getetag() } )
        BLOBManager.Close(handle)
