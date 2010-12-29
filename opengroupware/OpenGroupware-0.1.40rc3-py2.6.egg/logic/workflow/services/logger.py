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
from sqlalchemy       import and_
from time             import time
from StringIO         import StringIO
from coils.core       import *

class LoggerService(Service):
    __service__ = 'coils.workflow.logger'
    __auto_dispatch__ = True
    __is_worker__     = False

    def __init__(self):
        Service.__init__(self)

    def prepare(self):
        Service.prepare(self)
        self._ctx = AdministrativeContext({}, broker=self._broker)

    def _log_message(self, source, process_id, message, stanza=None,
                                                        timestamp=None,
                                                        category='undefined',
                                                        uuid=None):
        try:
            if (timestamp is None):
                timestamp = float(time())
            entry = ProcessLogEntry(source,
                                    process_id,
                                    message.strip(),
                                    stanza    = stanza,
                                    timestamp = timestamp,
                                    category  = category,
                                    uuid      = uuid)
            self._ctx.db_session().add(entry)
        except Exception, e:
            self.log.exception(e)
            self._ctx.rollback()
            return False
        else:
            self._ctx.commit()
            return True

    def do_log(self, parameter, packet):
        try:
            source     = Packet.Service(packet.source)
            process_id = int(packet.data.get('process_id'))
            message    = packet.data.get('message', None)
            stanza     = packet.data.get('stanza', None)
            category   = packet.data.get('category', 'undefined')
            uuid       = packet.uuid
            timestamp  = packet.time
        except Exception, e:
            self.log.exception(e)
            self._ctx.rollback()
            self.send(Packet.Reply(packet, {'status': 500, 'text': 'Failure to parse packet payload.'}))
        else:
            if (self._log_message(source, process_id, message, stanza=stanza,
                                                               timestamp=timestamp,
                                                               category=category,
                                                               uuid=uuid)):
                self.send(Packet.Reply(packet, {'status': 201, 'text': 'OK'}))
            else:
                self.send(Packet.Reply(packet, {'status': 500, 'text': 'Failure to record message.'}))

    def do_get_log(self, parameter, packet):
        # TODO: Support HTML & XML formats for response
        try:
            source     = Packet.Service(packet.source)
            process_id = int(parameter)
            format     = packet.data.get('format', 'text/plain')
            uuid       = packet.uuid
        except Exception, e:
            self.log.exception(e)
            self._ctx.rollback()
            self.send(Packet.Reply(packet, {'status': 500, 'text': 'Failure to parse packet payload.'}))
        else:
            db = self._ctx.db_session()
            query = db.query(ProcessLogEntry).\
                        filter(and_(ProcessLogEntry.process_id == process_id,
                                     ProcessLogEntry.stanza != None)).\
                        order_by(ProcessLogEntry.timestamp)
            logs = query.all()
            content = StringIO(u'')
            stanza = None
            start  = None
            for log in logs:
                if stanza != log.stanza:
                    if (stanza is not None):
                        content.write(u'\n')
                    stanza = log.stanza
                    content.write(u'Stanza {0}\n'.format(stanza.strip()))
                category = log.category
                if (category is None):
                    category = 'info'
                else:
                    category = category.strip()
                    if (category == 'start'):
                        start = log.timestamp
                content.write('{0}:{1}\n'.format(category.strip(), log.message))
                if ((category == 'complete') and (start is not None)):
                    content.write('duration:{0}s\n'.format(log.timestamp - start))
                    start = None
            self.send(Packet.Reply(packet, {'status': 200,
                                            'text': 'OK',
                                            'payload': content.getvalue()}))
            content = None
            db.commit()

    def do_reap(self, parameter, packet):
        process_id = int(parameter)
        db = self._ctx.db_session()
        try:
            db.query(ProcessLogEntry).\
                filter(ProcessLogEntry.process_id == process_id).\
                delete(synchronize_session='fetch')
        except Exception, e:
            self.log.exception(e)
            self.send(Packet.Reply(packet, {'status': 500, 'text': 'Failure to purge process log.'}))
        else:
            self._ctx.commit()
            self.send(Packet.Reply(packet, {'status': 201, 'text': 'OK'}))
