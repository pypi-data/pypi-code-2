# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.protocol.dav.foundation     import DAVObject

class EventObject(DAVObject):

    def __init__(self, parent, name, **params):
        DAVObject.__init__(self, parent, name, **params)

    def get_property_webdav_displayname(self):
        if (self.entity.title is None):
            return 'Appointment Id#{0}'.format(self.entity.object_id)
        else:
            return self.entity.title

    def get_property_webdav_owner(self):
        return u'<D:href>/dav/Contacts/{0}.vcf</D:href>'.format(self.entity.owner_id)

    def get_property_webdav_group(self):
        return None

    def get_property_caldav_calendar_data(self):
        return self.get_representation()

    @property
    def webdav_url(self):
        if (self.entity.caldav_uid is None):
            return '{0}/{1}.ics'.format(self.get_parent_path(), self.entity.object_id)
        else:
            return  '{0}/{1}'.format(self.get_parent_path(), self.entity.caldav_uid)

    def get_representation(self):
        if (self._representation is None):
            self._representation = self.context.run_command('appointment::get-as-vevent', object=self.entity)
        return self._representation
