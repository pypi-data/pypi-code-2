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
from xml.sax.saxutils                  import escape
from coils.net                         import DAVObject
from groupwareobject                   import GroupwareObject

class NoteObject(DAVObject, GroupwareObject):
    def __init__(self, parent, name, **params):
        DAVObject.__init__(self, parent, name, **params)

    def get_property_webdav_contenttype(self):
        if (self.request.user_agent.supports_memos):
            return 'calendar/ics'
        else:
            return 'text/plain'

    def get_property_caldav_calendar_data(self):
        return escape(self.get_representation())

    def get_property_webdav_owner(self):
        return u'<D:href>{0}</D:href>'.\
            format(self.request.user_agent.get_appropriate_href('/dav/Contacts/{0}.vcf'.format(self.entity.owner_id)))

    def do_GET(self):
        if (self.request.user_agent.supports_memos):
            DAVObject.do_GET(self)
        else:
            handle = self.context.run_command('note::get-handle', id=self.entity.object_id)
            self.request.stream_response(200,
                                         stream=handle,
                                         mimetype=self.entity.get_mimetype(),
                                         headers={ 'etag': self.get_property_webdav_getetag() } )
