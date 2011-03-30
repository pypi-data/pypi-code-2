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
import io, time
from datetime                          import datetime
# Core
from coils.core                        import *
from coils.net                         import *
# DAV Classses
from coils.protocol.dav.foundation     import DAVObject

class TaskObject(DAVObject):

    def __init__(self, parent, name, **params):
        DAVObject.__init__(self, parent, name, **params)

    def get_property_webdav_displayname(self):
        if (self.entity.name is None):
            return 'Task Id#{0}'.format(self.entity.object_id)
        else:
            return self.entity.name

    def get_property_webdav_name(self):
        return str(self.entity.object_id)

    #def get_property_GETCONTENTLENGTH(self):
        #if (self._get_representation()):
        #    return str(len(self.data))
    #    return str(self.entity.size)

    def get_property_webdav_contenttype(self):
        return 'calendar/ics'

    #def get_property_CREATIONDATE(self):
    #    if (self.entity.created is None):
    #        return datetime.now()
    #    else:
    #        return self.entity.created

    def get_property_webdav_getlastmodified(self):
        t = time.gmtime(self.entity.modified)
        return time.strftime("%a, %d %b %Y %H:%M:%S GMT", t)