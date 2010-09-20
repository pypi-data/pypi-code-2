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
from coils.core                        import *
import  coils.core.icalendar
from coils.protocol.dav.foundation     import DAVFolder, \
                                                OmphalosCollection, \
                                                OmphalosObject, \
                                                Parser, \
                                                BufferedWriter, \
                                                Multistatus
from coils.protocol.dav.groupware       import TaskObject
#from rss_feed                           import TasksRSSFeed


class TasksFolder(DAVFolder):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)
        self._start = None
        self._end   = None

    def _get_task_for_key(self, key):
        key = str(key).split('.')[0]
        if (key.isdigit()):
            object_id = int(key)
            return self.context.run_command('task::get', id=object_id)
        else:
            return None

    # PROP: GETCTAG

    def get_property_unknown_getctag(self):
        return self.get_property_caldav_getctag()

    def get_property_webdav_getctag(self):
        return self.get_property_caldav_getctag()

    def get_property_caldav_getctag(self):
        return self.get_ctag()

    def get_ctag(self):
        ''' Return a ctag appropriate for this object.
            Actual WebDAV objects should override this method '''
        db = self.context.db_session()
        query = db.query(CTag).filter(CTag.entity=='Job')
        ctags = query.all()
        if (len(ctags) == 0):
            return None
        query = None
        return ctags[0].ctag

    def _load_self(self):
        tasks = self.context.run_command('project::get-tasks', project=self.entity)
        self.data = { }
        for task in tasks:
            self.data[u'{0}.vcf'.format(task.object_id)] = [task]
        return True

    def object_for_key(self, name):
        if (name == 'todo.rss'):
            return TasksRSSFeed(self, 'todo', request=self.request,
                                               context=self.context)
        elif (self.load_self()):
            if (name in self.data):
                return TaskObject(self, name, entity=self.data[name][0],
                                               location=u'/dav/Tasks/{0}'.format(name),
                                               context=self.context,
                                               request=self.request)
        self.no_such_path()

    def supports_PUT(self):
        return True

    def do_PUT(self, name):
        ''' Process a PUT request '''
        self.log.debug('PUT request with name {0}'.format(name))
        event = self._get_event_for_key(name)
        if (event is not None):
            object_id = event.object_id
        else:
            object_id = None
        if_etag = self.request.headers.get('If-Match', None)
        if (if_etag is None):
            self.log.warn('Client issued a put operation with no If-Match!')
        payload = self.request.get_request_payload()
        values = coils.core.icalendar.Parser.Parse(payload, self.context)
        if (values):
            data = values[0]
            if (('object_id' in data) and (object_id is None)):
                object_id = data['object_id']
            if (object_id is None):
                a = self.context.run_command('appointment::new', values=data)
                self.context.commit()
                self.request.send_response(201, 'Created')
                self.request.send_header('Etag', '{0}:{1}'.format(a.object_id, a.version))
                self.request.send_header('Location', '/dav/Calendar/{0}.ics'.format(a.object_id))
                self.request.end_headers()
            else:
                a = self.context.run_command('appointment::get', id=data['object_id'])
                a = self.context.run_command('appointment::set', object=appointment,
                                                                 values=data)
                self.context.commit()
                self.request.send_response(204, 'No Content')
                self.request.send_header('Etag', '{0}:{1}'.format(a.object_id, a.version))
                self.request.end_headers()
