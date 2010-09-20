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
from StringIO                          import StringIO
from coils.protocol.dav.foundation     import DAVObject

class GroupwareObject(object):

    def _get_privileges(self):
        data = self._ctx.access_manager.filter_by_access(self._ctx, 'r', data)

    def get_property_webdav_current_user_privilege_set(self):
        rights = self.context.access_manager.access_rights(self.context, self.entity)
        result = StringIO()
        result.write(u'<privilege>')
        if ('r' in rights): result.write(u'<read/>')
        # TODO: Once we have PROPATCH support we should add
        #        "write" and "write-properties" privileges
        # ????: unlock, read-acl, write-acl [part of write?]
        #       bind & unbind are only for folders
        if ('w' in rights): result.write(u'<write-content/>')
        result.write(u'<read-current-user-privilege-set/>')
        result.write(u'</privilege>')
        result = result.getvalue()
        return result

    def get_property_webdav_current_user_principal(self):
        # RFC5397: WebDAV Current Principal Extension
        return u'<href>/dav/Contacts/{0}.vcf</href>'.format(self.context.account_id)
