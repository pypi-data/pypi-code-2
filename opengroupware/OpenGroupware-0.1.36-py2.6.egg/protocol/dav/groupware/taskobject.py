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

    #def get_property_webdav_displayname(self):
    #    if (self.entity.name is None):
    #        return 'Task Id#{0}'.format(self.entity.object_id)
    #    else:
    #        return self.entity.name

    @property
    def webdav_url(self):
        if (self.entity.caldav_uid is None):
            return u'{0}/{1}.ics'.format(self.get_parent_path(), self.entity.object_id)
        else:
            return  u'{0}/{1}'.format(self.get_parent_path(), self.entity.caldav_uid)

    def get_representation(self):
        if (self._representation is None):
            self._representation = self.context.run_command('task::get-as-vtodo', object=self.entity)
        return self._representation

    def get_property_webdav_owner(self):
        return u'<href>/dav/Contacts/{0}.vcf<href>'.format(self.entity.owner_id)

    def get_property_webdav_contenttype(self):
        return 'calendar/ics'

    def get_property_caldav_calendar_data(self):
        return self.get_representation()

    #def get_property_CREATIONDATE(self):
    #    if (self.entity.created is None):
    #        return datetime.now()
    #    else:
    #        return self.entity.created

    def get_property_webdav_getlastmodified(self):
        if (self.entity.modified is None):
            return datetime.fromtimestamp(0).strftime("%a, %d %b %Y %H:%M:%S GMT")
        else:
            return datetime.fromtimestamp(self.entity.modified).strftime("%a, %d %b %Y %H:%M:%S GMT")
