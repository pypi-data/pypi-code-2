#
# Copyright (c) 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
from email.Parser import Parser
from coils.core  import *
import smtpd
import asyncore
import threading
import pprint


class SMTPServer(smtpd.SMTPServer):

    def __init__(self, manager):
        self.manager = manager
        sd = ServerDefaultsManager()
        SMTP_ADDR = sd.string_for_default('SMTPListenAddress', '127.0.0.1')
        SMTP_PORT = sd.integer_for_default('SMTPListenPort', 9000)
        smtpd.SMTPServer.__init__(self, (SMTP_ADDR, SMTP_PORT), None)

    def process_message(self, peer, from_, to_, data):
        # TODO: Verify one of the recipients is a candidate
        # TODO: discard messgaes over a given size?
        # TODO: discard messages with more tha n recipients?
        self.manager.enqueue_message((from_, to_, data))


class SMTPService(Service):
    __service__ = 'coils.smtpd'
    __auto_dispatch__ = True
    __is_worker__     = True

    @property
    def queue(self):
        return self._queue

    @property
    def queue_lock(self):
        return self._queue_lock

    @property
    def smtp_prefix(self):
        return self._prefix

    @property
    def ctx(self):
        return self._ctx

    def prepare(self):
        try:
            sd = ServerDefaultsManager()
            self._prefix= sd.string_for_default('SMTPAddressPrefix', 'ogo').lower()
            self._queue = [ ]
            self._queue_lock = threading.Lock()
            self._smptd = SMTPServer(self)
            self._thread = threading.Thread(target=lambda:asyncore.loop())
            self._thread.start()
            self._ctx = NetworkContext(broker=self._broker)
        except Exception, e:
            self.log.warn('Exception in SMTP component prepare')
            self.log.exception(e)
            raise e

    def shutdown(self):
        self._smtpd.stop()
        Service.shutdown(self)

    def enqueue_message(self, message):
        with self.queue_lock:
            self.queue.append(message)

    def work(self):
        self.log.info('SMTP  *work*')
        # TODO: Component check should be a time-based, not iteration based, component
        with self.queue_lock:
            self.log.info('SMTP service checking message queue')
            while self.queue:
                p = Parser()
                data = self.queue.pop()
                self.log.info('SMTP server found message!')
                try:
                    recipient = None
                    message = p.parsestr(data[2])
                    for recipient in data[1]:
                        recipient = recipient.lower().strip()
                        self.log.debug('checking recipient {0}'.format(recipient))
                        x = recipient.split('@')[0].split('+', 1)
                        if (len(x) == 2):
                            if (x[0].lower() == self.smtp_prefix):
                                recipient = x[1]
                                break
                    else:
                        self.log.warn('Discarding message, no matching recipients')
                except Exception, e:
                    self.log.info('SMTP failed to parse message')
                    self.log.exception(e)
                else:
                    self.log.info('SMTP sending administrative message')
                    try:
                        '''self.send_administrative_notice(subject='Received messgae via SMTP',
                                                        message=pprint.pformat((recipient, data[0], data[1], data[2])),
                                                        urgency=4,
                                                        category='network',
                                                        attachments=[])'''
                        self.process_recipient(data[0], recipient, message)
                    except Exception, e:
                        self.log.exception(e)


    def process_recipient(self, from_, to_, message):
        targets = to_.split('+')
        if (len(targets) == 1):
            try:
                object_id = int(targets[0])
            except:
                self.log.warn('Unable to convert single recipient target "{0}" into an integer value'.format(target[0]))
            else:
                # TODO: Support e-mails to entities, like tasks
                pass
        elif (len(targets) == 2):
            if (targets[0] == 'wf'):
                # This is meant to trigger a workflow!
                route = self.ctx.run_command('route::get', name=targets[1])
                if (route is not None):
                    self.log.warn('Creating process from route routeId#{0}'.format(route.object_id))
                    if (message.is_multipart()):
                        message = 'A multipart message was submitted to routeId#{0}'.format(route.object_id)
                        self.send_administrative_notice(subject='Multipart message submitted to workflow',
                                    message=message,
                                    urgency=8,
                                    category='workflow',
                                    attachments=[])
                    else:
                        try:
                            payload = message.get('Subject')
                        except Exception, e:
                            self.log.exception(e)
                        else:
                            process =  self.ctx.run_command('process::new', values={ 'route_id': route.object_id,
                                                                                     'data':     payload,
                                                                                     'priority': 210 } )
                            self.ctx.commit()
                            self.ctx.run_command('process::start', process=process)
                            message = 'Requesting to start ProcessId#{0} / RouteId#{0}.'.format(process.object_id, route.object_id)
                            self.log.info(message)
                            '''self.send_administrative_notice(subject='Process created via SMTP',
                                        message=message,
                                        urgency=5,
                                        category='workflow',
                                        attachments=[])'''
                else:
                    message = 'No such route as {0} available.'.format(targets[1])
                    self.log.warn(message)
                    self.send_administrative_notice(subject='Unable to marshall route requested via SMTP',
                                message=message,
                                urgency=7,
                                category='workflow',
                                attachments=[])
            else:
                self.log.warn('Nested outer target type of "{0}" not recognized'.format(targets[0]))
        else:
            self.log.warn('Target of messages has too many components')
