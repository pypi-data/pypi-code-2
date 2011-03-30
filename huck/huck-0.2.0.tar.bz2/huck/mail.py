# Copyright 2011 Silas Sewell
# Copyright 2010 Alexandre Fiori
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Implementation of e-mail Message and SMTP with and without SSL"""

import os.path
from cStringIO import StringIO
from OpenSSL.SSL import SSLv3_METHOD

from email import Encoders
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.Utils import COMMASPACE, formatdate

from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.ssl import ClientContextFactory
from twisted.mail.smtp import ESMTPSenderFactory

class Message(object):

    def __init__(self, from_addr, to_addrs, subject, message, mime='text/plain', charset='utf-8'):
        self.subject = subject
        self.from_addr = from_addr
        self.to_addrs = [to_addrs] if isinstance(to_addrs, basestring) else to_addrs

        self.msg = None
        self.__cache = None
        self.message = MIMEText(message)
        self.message.set_charset(charset)
        self.message.set_type(mime)

    def __str__(self):
        return '<Message: %s => %s: %s>' % (
            self.from_addr,
            ','.join(self.to_addrs),
            self.subject,
        )

    def attach(self, path, mime=None, charset=None, content=None):
        name = os.path.basename(path)

        if content is None:
            with open(path) as f:
                content = f.read()

        if not isinstance(content, basestring):
            raise TypeError('Unable to handle content: %s' % type(content))
        
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(content)
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % name)
        
        if mime is not None:
            part.set_type(mime)

        if charset is not None:
            part.set_charset(charset)

        if self.msg is None:
            self.msg = MIMEMultipart()
            self.msg.attach(self.message)

        self.msg.attach(part)

    def render(self):
        if self.msg is None:
            self.msg = self.message

        self.msg['Subject'] = self.subject
        self.msg['From'] = self.from_addr
        self.msg['To'] = COMMASPACE.join(self.to_addrs)
        self.msg['Date'] = formatdate(localtime=True)

        return StringIO(self.msg.as_string())

    def send(self, host, port=None, username=None, password=None, tls=False):
        """Send email message"""
        if tls:
            if port is None:
                port = 587
            contextFactory = ClientContextFactory()
            contextFactory.method = SSLv3_METHOD
        else:
            if port is None:
                port = 25
            contextFactory = None

        d = Deferred()

        factory = ESMTPSenderFactory(
            username,
            password,
            self.from_addr,
            self.to_addrs,
            self.render(),
            d,
            contextFactory=contextFactory,
            requireAuthentication=username and password,
            requireTransportSecurity=tls,
        )
        reactor.connectTCP(host, port, factory)

        return d
