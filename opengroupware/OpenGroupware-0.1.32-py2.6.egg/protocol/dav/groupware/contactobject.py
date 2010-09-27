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
from groupwareobject                   import GroupwareObject

'''
NOTE: 2010-09-14 Implemented WebDAV "owner" property RFC2744 (Access Control)
                 Implemented WebDAV "group-membership" property RFC2744 (Access Control)
                 Implemented WebDAV "group" property RFC2744 (Access Control)

TODO: DAV:current-user-privilege-set
       DAV:acl
       DAV:acl-restrictions
'''

class ContactObject(DAVObject, GroupwareObject):

    def __init__(self, parent, name, **params):
        DAVObject.__init__(self, parent, name, **params)

    @property
    def webdav_url(self):
        if (self.entity.carddav_uid is None):
            return '{0}/{1}.vcf'.format(self.get_parent_path(), self.entity.object_id)
        else:
            return  '{0}/{1}'.format(self.get_parent_path(), self.entity.carddav_uid)

    def get_property_webdav_principal_url(self):
        return u'<href>/dav/Contacts/{0}.vcf</href>'.format(self.entity.object_id)

    def get_property_webdav_owner(self):
        return u'<href>/dav/Contacts/{0}.vcf</href>'.format(self.entity.owner_id)

    def get_property_webdav_group(self):
        return None

    def get_property_webdav_group_membership(self):
        if (self.entity.is_account):
            teams = self.context.run_command('team::get', member_id=self.entity.object_id)
            groups = [ ]
            for team in teams:
                groups.append('<href>/dav/Teams/{0}.vcf</href>'.format(team.object_id))
            return u''.join(groups)
        else:
            return None

    def get_representation(self):
        if (self._representation is None):
            self._representation = self.context.run_command('contact::get-as-vcard', object=self.entity)
        return self._representation

    #def get_property_CREATIONDATE(self):
    #    if (self.entity.created is None):
    #        return datetime.now()
    #    else:
    #        return self.entity.created
