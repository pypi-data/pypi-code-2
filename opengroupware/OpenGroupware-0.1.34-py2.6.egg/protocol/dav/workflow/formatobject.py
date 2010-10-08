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
import io
from datetime           import datetime
# Core
from coils.core         import *
from coils.net          import *
# DAV Classses
from coils.protocol.dav.foundation     import *

class FormatObject(DAVObject):
    ''' Represents a workflow message in a process with a DAV hierarchy. '''

    def __init__(self, parent, name, **params):
        DAVObject.__init__(self, parent, name, **params)
        self.log.debug(' FormatObject named {0} is entity {1}'.format(name, repr(self.entity)))
        self._yaml = None

    def get_yaml_content(self):
        if (self._yaml is None):
            self._yaml = self.entity.as_yaml()
        return self._yaml

    def get_property_webdav_getetag(self):
        return u'{0}'.format(self.entity.get_name())

    def get_property_webdav_displayname(self):
        return u'{0}'.format(self.entity.get_name())

    def get_property_webdav_getcontentlength(self):
        return str(len(self.get_yaml_content()))

    def get_property_webdav_getcontenttype(self):
        return 'text/plain'

    def get_property_webdav_creationdate(self):
       return datetime.now()

    def do_HEAD(self):
        self.request.send_response(201, 'OK')
        self.request.send_header('Content-Length', self.get_property_webdav_getcontentlength())
        self.request.send_header('etag', self.get_property_webdav_getetag())
        self.request.send_header('Content-Type', self.get_property_webdav_getcontenttype())
        self.request.end_headers()

    def do_GET(self):
        self.request.send_chunked_data({ 'etag': self.get_property_webdav_getetag() },
                                       self.get_property_webdav_getcontenttype(),
                                       self.get_yaml_content())
