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
from datetime                          import datetime, timedelta
from coils.foundation                  import CTag
from coils.core                        import Appointment
from coils.protocol.dav.foundation     import DAVFolder, \
                                                OmphalosCollection, \
                                                OmphalosObject, \
                                                StaticObject, \
                                                Parser, \
                                                BufferedWriter, \
                                                Multistatus
from taskobject                        import TaskObject
from rss_feed                          import TasksRSSFeed
from groupwarefolder                   import GroupwareFolder


class TasksFolder(DAVFolder, GroupwareFolder):

    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)
        self._start = None
        self._end   = None

    def get_property_webdav_owner(self):
        return u'<href>/dav/Contacts/{0}.vcf</href>'.format(self.context.account_id)

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
                if (self._start is None): self._start = datetime.now() - timedelta(days=1)
                if (self._end is None): self._end   = datetime.now() + timedelta(days=90)
                for task in result:
                    if ((self._start is not None) or (self._end is not None)):
                        #TODO: Implement date-range scoping
                        pass
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

    def do_OPTIONS(self):
        ''' Return a valid WebDAV OPTIONS response '''
        self.request.send_response(200, 'OpenGroupware.org COILS')
        #methods = [ 'HEAD', 'OPTIONS' ]
        #for method in self.get_methods():
        #    if (self.supports_operation(method)):
        #        methods.append(method)
        self.request.send_header('Allow', 'OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, COPY, MOVE')
        self.request.send_header('Allow', 'PROPFIND, PROPPATCH, LOCK, UNLOCK, REPORT, ACL')
        #self.request.send_header('Allow', ','.join(methods))
        #methods = None
        self.request.send_header('Content-length', '0')
        self.request.send_header('DAV', '1, 2, access-control, calendar-access')
        self.request.send_header('MS-Author-Via', 'DAV')
        self.request.end_headers()

    def do_REPORT(self):
        ''' Preocess a report request '''
        payload = self.request.get_request_payload()
        self.log.debug('REPORT REQUEST: %s' % payload)
        parser = Parser.report(payload)
        if (parser.report_name == 'calendar-query'):
            self._start = parser.parameters.get('start', None)
            self._end   = parser.parameters.get('end', None)
            d = {}
            if (self.load_contents()):
                for child in self.get_children():
                    if child.caldav_uid is None:
                        name = u'{0}.ics'.format(child.object_id)
                    else:
                        name = child.caldav_uid
                    x = TaskObject(self, name, entity=child,
                                               location='/dav/Tasks/{0}.ics'.format(child.object_id),
                                               context=self.context,
                                               request=self.request)
                    d[x.location] = x
                self.request.send_response(207, 'Multistatus')
                self.request.send_header('Content-Type', 'text/xml')
                w = BufferedWriter(self.request.wfile, False)
                Multistatus.generate(d, parser.properties, w)
                self.request.send_header('Content-Length', str(w.getSize()))
                self.request.end_headers()
                w.flush()
        elif (parser.report_name == 'calendar-multiget'):
            d = {}
            if (self.load_contents()):
                for href in parser.references:
                    if (href not in d):
                        key = href.split('/')[-1]
                        try:
                            entity = self.get_object_for_key(key)
                            d[href] = entity
                        except NoSuchPathException, e:
                            self.log.debug('Missing resource {0} in collection'.format(key))
                        except Exception, e:
                            self.log.exception(e)
                            raise e
                self.request.send_response(207, 'Multistatus')
                self.request.send_header('Content-Type', 'text/xml')
                w = BufferedWriter(self.request.wfile, False)
                Multistatus.generate(d, parser.properties, w)
                self.request.send_header('Content-Length', str(w.getSize()))
                self.request.end_headers()
                w.flush()
        else:
            raise CoilsException('Unsupported report {0} in {1}'.format(parser.report_name, self))