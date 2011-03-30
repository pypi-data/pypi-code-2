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
import hashlib
from coils.protocol.dav.foundation     import DAVFolder, DAVObject
from coils.protocol.dav.foundation     import DAVFolder
from coils.protocol.dav.foundation     import EmptyFolder
from coils.protocol.dav.foundation     import OmphalosCollection
from coils.protocol.dav.foundation     import OmphalosObject
from coils.protocol.dav.foundation     import StaticObject
from projectfolder                     import ProjectFolder
from rss_feed                          import ProjectTaskActionsRSSFeed

class ProjectsFolder(DAVFolder):
    ''' Provides a WebDAV collection containing all the projects (as
        subfolders) which the current account has access to,'''

    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)

    def _load_contents(self):
        ''' Enumerates projects using account::get-projects.'''
        content = self.context.run_command('account::get-projects')
        if (content is not None):
           for project in content:
               self.insert_child(project.number, project, alias=project.object_id)
        else:
            return False
        return True

    def _get_project_for_key(self, key):
        if (self.load_contents()):
            if (self.has_child(key)):
                return self.get_child(key)
        try:
            object_id = int(str(key).split('.')[0])
        except:
            return None
        return self.context.run_command('project::get', id=object_id)

    def get_property_unknown_getctag(self):
        return self.get_property_caldav_getctag()

    def get_property_webdav_getctag(self):
        return self.get_property_caldav_getctag()

    def get_property_caldav_getctag(self):
        return self._get_ctag()

    def _get_ctag(self):
        if (self.load_contents()):
            m = hashlib.md5()
            for entry in self.get_children():
                m.update('{0}:{1}'.format(entry.object_id, entry.version))
            return unicode(m.hexdigest())
        return u'0'

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if (name == '.ctag'):
            # TODO: 
            return StaticObject(self, '.ctag', context=self.context,
                                                request=self.request,
                                                payload=self._get_ctag(),
                                                mimetype='text/plain')
        elif ((name == '.json') and (self.load_contents())):
            # Get an index of the folder as an Omphalos collection
            return OmphalosCollection(self,
                                       name,
                                       data=self.get_children(),
                                       context=self.context,
                                       request=self.request)
        elif ((name[-5:] == '.json') or
              (name[-4:] == '.xml') or
              (name[-5:] == '.yaml')):
            # Get a project in Omphalos representation
            entity = self._get_project_for_key(name)
            if (entity is not None):
               return OmphalosObject(self,
                                      name,
                                      entity=entity,
                                      context=self.context,
                                      request=self.request)
        elif (name == 'actions.rss'):
            # Task actions RSS feed
            return ProjectTaskActionsRSSFeed(self, name, None,
                                              request=self.request,
                                              context=self.context)
        if (auto_load_enabled):
            if (self.load_contents()):
                if (self.has_child(name)):
                   # WebDAV collection
                    x = self.get_child(name)
                    x = ProjectFolder(self, x.number,
                                      entity=x,
                                      request=self.request,
                                      context=self.context)
                    return x
                elif (('(' in name) or (')' in name)):
                    name = name.replace('(', '%28').replace(')', '%29')
                    return self.object_for_key(name, auto_load_enabled=auto_load_enabled, is_webdav=is_webdav)
        self.no_such_path()
