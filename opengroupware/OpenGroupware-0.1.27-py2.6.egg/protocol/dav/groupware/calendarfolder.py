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
from datetime                          import datetime, timedelta
from coils.foundation                  import CTag, ServerDefaultsManager
from coils.core                        import Appointment, NoSuchPathException
import  coils.core.icalendar
from coils.protocol.dav.foundation     import DAVFolder, \
                                                OmphalosCollection, \
                                                OmphalosObject, \
                                                Parser, \
                                                BufferedWriter, \
                                                Multistatus
from groupwarefolder                   import GroupwareFolder
from eventobject                       import EventObject


'''
    TODO: Implement WebDAV "group" property RFC2744 (Access Control)
    NOTES: 2010-08-09 Implemented WebDAV "owner" property RFC2744 (Access Control)
'''

class CalendarFolder(DAVFolder, GroupwareFolder):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)
        self._start = None
        self._end   = None

    def supports_PUT(self):
        return True

    def supports_DELETE(self):
        return True

    def supports_REPORT(self):
        return True

    def _get_overview_range(self, **params):
        events = self.context.run_command('appointment::get-overview-range', **params)
        return events

    def _get_personal_range(self, **params):
        events = self.context.run_command('appointment::get-range', **params)
        return events

    def _get_calendar_range(self, **params):
        events = self.context.run_command('appointment::get-calendar', **params)
        return events

    # PROP: OWNER

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
        return self.get_ctag_for_entity('Date')

    @property
    def is_collection_folder(self):
        if (self.is_favorites_folder):
            return True
        if (self.parent.__class__.__name__ == 'CalendarFolder'):
            # Subfolder, contains an event collection
            return True
        return False

    def _load_contents(self):
        # TODO: Read range from server configuration
        self.log.info('Loading content in calendar folder for name {0}'.format(self.name))
        if (self.is_collection_folder):
            if (self._start is None): self._start = datetime.now() - timedelta(days=1)
            if (self._end is None): self._end   = datetime.now() + timedelta(days=90)
            if (self.name == 'Personal'):
                events = self._get_personal_range(start = self._start,
                                                  end   = self._end,
                                                  visible_only = True)
            else:
                # TODO: We assume non-Personal is Overview
                events = self._get_overview_range(start = self._start,
                                                  end   = self._end,
                                                  visible_only = True)
            for event in events:
                if (event.caldav_uid is None):
                    self.insert_child(event.object_id, event, alias='{0}.ics'.format(event.object_id))
                else:
                    self.insert_child(event.object_id, event, alias=event.caldav_uid)
        else:
            self.insert_child('Personal', CalendarFolder(self, 'Personal', context=self.context, request=self.request))
            self.insert_child('Overview', CalendarFolder(self, 'Overview', context=self.context, request=self.request))
            #ud = ServerDefaultsManager()
            #calendars = ud.default_as_list('LSCalendars')
            #for calendar in calendars:
            #    self.data[calendar] = CalendarFolder(self, calendar, context=self.context, request=self.request)
        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if (name == '.ctag'):
            if (self.is_collection_folder):
                return self.get_ctag_representation(self.get_ctag_for_collection())
            else:
                return self.get_ctag_representation(self.get_ctag_for_entity('Date'))
        elif ((name == '.json') and (self.load_contents())):
            return self.get_collection_representation(name, self.get_children())
        else:
            location = None
            if (self.is_collection_folder):
                if (self.load_contents() and (auto_load_enabled)):
                    appointment = self.get_child(name)
                    if (appointment is None):
                        (object_id, payload_format, appointment, values) = self.get_appointment_for_key(name)
                location = '/dav/Calendar/{0}'.format(name)
            else:
                self.load_contents()
                result = self.get_child(name)
                if (result is not None):
                    return result
                (object_id, payload_format, appointment, values) = self.get_appointment_for_key(name)
            if (appointment is not None):
                return self.get_entity_representation(name, appointment, location=location,
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
                    x = EventObject(self, name, entity=child,
                                                location='/dav/Calendar/{0}.ics'.format(child.object_id),
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

    def apply_permissions(self, appointment):

        pass

    def do_PUT(self, name):
        ''' Process a PUT request '''
        self.log.debug('PUT request with name {0}'.format(name))
        payload = self.request.get_request_payload()
        (object_id, payload_format, appointment, payload_values) = self.get_appointment_for_key_and_content(name, payload)
        if_etag = self.request.headers.get('If-Match', None)
        if (if_etag is None):
            self.log.warn('Client issued a put operation with no If-Match!')
        else:
            # TODO: Implement If-Match test
            self.log.warn('If-Match test not implemented at {0}'.format(self.url))
        if (appointment is None):
            # Create appointment
            appointment = self.context.run_command('appointment::new', values=payload_values)
            appointment.caldav_uid = name
            self.apply_permissions(appointment)
            self.context.commit()
            self.request.send_response(201, 'Created')
            self.request.send_header('Etag', '{0}:{1}'.format(appointment.object_id, appointment.version))
            self.request.send_header('Location', '/dav/Calendar/{0}.ics'.format(appointment.object_id))
            self.request.end_headers()
        else:
            self.context.run_command('appointment::set', object=appointment,
                                                         values=payload_values)
            self.context.commit()
            self.request.send_response(204, 'No Content')
            self.request.send_header('Etag', '{0}:{1}'.format(appointment.object_id, appointment.version))
            self.request.end_headers()

    def do_DELETE(self, name):
        ''' Process a DELETE request '''
        self.log.debug('DELETE request with name {0}'.format(name))
        (object_id, payload_format, appointment, payload_values) = self.get_appointment_for_key(name)
        if (appointment is not None):
            if(self.context.run_command('appointment::delete', object=appointment)):
                self.context.commit()
                self.request.send_response(204, 'No Content')
                self.request.end_headers()
                return
        self.no_such_path()