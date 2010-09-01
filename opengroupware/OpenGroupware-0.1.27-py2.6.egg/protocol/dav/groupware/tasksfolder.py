#
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
import datetime, hashlib
from coils.foundation                  import CTag
from coils.core                        import Appointment
from coils.protocol.dav.foundation     import DAVFolder, \
                                                OmphalosCollection, \
                                                OmphalosObject, \
                                                StaticObject
from taskobject                        import TaskObject
from rss_feed                          import TasksRSSFeed
from groupwarefolder                   import GroupwareFolder


class TasksFolder(DAVFolder, GroupwareFolder):

    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)

    def get_property_webdav_owner(self):
        return u'<D:href>/dav/Contacts/{0}.vcf</D:href>'.format(self.context.account_id)

    # PROP: GETCTAG

    def get_property_unknown_getctag(self):
        return self.get_property_caldav_getctag()

    def get_property_webdav_getctag(self):
        return self.get_property_caldav_getctag()

    def get_property_caldav_getctag(self):
        return self.get_ctag()

    def get_ctag(self):
        if (self.is_collection_folder):
            return self.get_ctag_for_collection()
        else:
            return self.get_ctag_for_entity('Job')

    def _load_contents(self):
        # TODO: Read range from server configuration
        self.log.info('Loading content in task folder for name {0}'.format(self.name))
        if (self.is_collection_folder):
            result = None
            if (self.is_project_folder):
                result = self.context.run_command('project::get-tasks', project=self.entity)
            if (self.is_favorites_folder):
                # Not supported
                raise NotImplementedException('Favoriting of tasks is not supported.')
            elif (self.name == 'Delegated'):
                result = self.context.run_command('task::get-delegated')
            elif (self.name == 'ToDo'):
                result = self.context.run_command('task::get-todo')
            elif (self.name == 'Assigned'):
                #TODO: Implement assigned tasks
                result = [ ]
            elif (self.name == 'Archived'):
                result = self.context.run_command('task::get-archived')
            if (result is None):
                return False
            else:
                self.data = { }
                for task in result:
                    self.insert_child(task.object_id, task, alias='{0}.ics'.format(task.object_id))
        else:
            self.insert_child('Delegated', TasksFolder(self, 'Delegated', context=self.context, request=self.request))
            self.insert_child('ToDo',      TasksFolder(self, 'ToDo',      context=self.context, request=self.request))
            self.insert_child('Archived',  TasksFolder(self, 'Archived',  context=self.context, request=self.request))
            self.insert_child('Assigned',  TasksFolder(self, 'Assigned',  context=self.context, request=self.request))
        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if (name == '.ctag'):
            if (self.is_collection_folder):
                return self.get_ctag_representation(self.get_ctag_for_collection())
            else:
                return self.get_ctag_representation(self.get_ctag_for_entity('Job'))
        elif ((name == '.json') and (self.load_contents())):
            return self.get_collection_representation(name, self.get_children())
        elif (name == '.content.json'):
            return self.get_collection_representation(name, self.get_children(), rendered=True)
        else:
            if (self.is_collection_folder):
                if (self.load_contents() and (auto_load_enabled)):
                    task = self.get_child(name)
                    location = '/dav/Tasks/{0}'.format(name)
            else:
                self.load_contents()
                result = self.get_child(name)
                if (result is not None):
                    return result
                (object_id, payload_format, task, values) = self.get_tasks_for_key(name)
            if (task is not None):
                return self.get_entity_representation(name, task, location=location,
                                                                   is_webdav=is_webdav)
        self.no_such_path()