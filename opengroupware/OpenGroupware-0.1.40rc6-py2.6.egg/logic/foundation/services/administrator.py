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
#
import uuid
from email.mime.text     import MIMEText
from email.Utils         import COMMASPACE, formatdate
from coils.core          import *

class AdministratorService (Service):
    __service__ = 'coils.administrator'
    __auto_dispatch__ = True

    def __init__(self):
        Service.__init__(self)

    def prepare(self):
        Service.prepare(self)
        self._ctx = AdministrativeContext({}, broker=self._broker)
        self._sd = ServerDefaultsManager()
        server_uuid_prop = self._ctx.property_manager.get_server_property('http://www.opengroupware.us/global', 'clusterGUID')
        if (server_uuid_prop is None):
            self._cluster_guid = '{{{0}}}'.format(str(uuid.uuid4()))
            self._ctx.property_manager.set_server_property('http://www.opengroupware.us/global', 'clusterGUID', self._cluster_guid)
            self._ctx.commit()
        else:
            self._cluster_guid = server_uuid_prop.get_value()
            server_uuid_prop = None

    @property
    def administrative_email(self):
        return self._sd.string_for_default('AdministrativeEMailAddress', value='root@localhost')

    def do_get_server_defaults(self, parameter, packet):
        self.send(Packet.Reply(packet, {'status':   200,
                                        'text':     'OK',
                                        'GUID':     self._cluster_guid,
                                        'defaults': self._sd.defaults } ) )

    def do_get_cluster_guid(self, parameter, packet):
        self.send(Packet.Reply(packet, {'status':   200,
                                        'text':     'OK',
                                        'GUID':     self._cluster_guid } ) )

    def do_notify(self, parameter, packet):
        try:
            self.log.info('Received a request to notify administrator')
            category = packet.data.get('category', 'unspecified')

            urgency  = packet.data.get('urgency', 5)

            subject  = packet.data.get('subject', None)
            if (subject is None):
                subject = u'[OpenGrouware] Administrative Notice {0}'.format(packet.uuid)
            else:
                subject = u'[OpenGrouware] {0}'.format(subject)

            message = unicode(packet.data.get('message'))
            
            message            = MIMEText(message)
            message['Subject'] = subject
            message['From']    = ''
            message['To']      = self.administrative_email
            message['Date']    = formatdate(localtime=True)
            message['X-Opengroupware-Alert'] = packet.uuid
            message['X-Opengroupware-Cluster-GUID'] = self._cluster_guid
            SMTP.send('', [ self.administrative_email ], message)
            self.log.info('Message sent to administrator.')
        except Exception, e:
            # TODO: log something and make response more informative
            self.log.exception(e)
            self.send(Packet.Reply(packet, {'status': 500,
                                            'text': 'Failure'}))
        else:
            self.send(Packet.Reply(packet, {'status': 201, 'text':
                                            'OK'}))
