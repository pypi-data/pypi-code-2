# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import BaseHTTPServer
import SimpleHTTPServer
import gocept.lms
import gocept.lms.client
import os.path
import socket
import unittest
import zope.app.appsetup.product
import zope.app.testing.functional
import zope.sendmail.interfaces
import zope.testing.doctest


ftesting_zcml = os.path.join(
    os.path.dirname(gocept.lms.__file__), 'ftesting.zcml')
FunctionalLayer = zope.app.testing.functional.ZCMLLayer(
    ftesting_zcml, __name__, 'FunctionalLayer', allow_teardown=True)


flags = (zope.testing.doctest.ELLIPSIS |
         zope.testing.doctest.NORMALIZE_WHITESPACE |
         zope.testing.doctest.REPORT_NDIFF |
         zope.testing.doctest.INTERPRET_FOOTNOTES)


class TestHTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silence, please.
        pass

    def do_GET(self):
        if self.path == '/agent':
            self.send_response(599, self.headers['user-agent'])
            self.end_headers()
            return ''
        return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)


class DummyMailDelivery(object):

    zope.interface.implements(zope.sendmail.interfaces.IMailDelivery)

    messages = []

    def send(self, fromaddr, toaddr, msg):
        print "(%s -> %s)" % (fromaddr, toaddr)
        is_base64 = False
        lines = iter(msg.splitlines(True))
        headers = []
        for line in lines:
            print line,
            headers.append(line)
            if not line.strip():
                break
            if line.strip() == "Content-Transfer-Encoding: base64":
                is_base64 = True
        body = "".join(lines)
        print body
        self.messages.append((fromaddr, toaddr, headers, body))

    @classmethod
    def reset(cls):
        cls.messages = []


zope.testing.cleanup.addCleanUp(DummyMailDelivery.reset)


class XMLRPCDummy(object):

    fail_update = False

    def __init__(self):
        self.log = []

    def __call__(self, url):
        self.log.append('Connect: %s' % url)
        return self

    def updateManyStates(self, id, password, notifications):
        if self.fail_update:
            raise Exception('Client unreachable')
        self.log.append('Update many states: %s - %s' %
          (id, len(notifications)))

    def show_log(self):
        print '\n'.join(self.log)
        self.log = []

    def xmlrpc_getAllLinks(self, id, password):
        self.log.append('Get all links')
        return ['http://example.com/1',
                'http://example.com/3']


def install_xmlrpcdummy():
    gocept.lms.client.ServerProxy = dummy = XMLRPCDummy()
    return dummy


def setup(test):
    config = zope.app.appsetup.product._configs['gocept.lms'] = {}
    config['lms-name'] = 'Test LMS'
    config['lms-email-address'] = 'lms@gocept.testing'
    config['lms-xmlrpc-address'] = 'http://lms.testing/'
    config['lms-send-cc-to'] = 'admin@gocept.testing otheradmin@gocept.testing'

def test_suite():
    functional = zope.app.testing.functional.FunctionalDocFileSuite(
        'app.txt',
        'url.txt',
        'check.txt',
        'ftp.txt',
        'http.txt',
        'munin.txt',
        'notify.txt',
        'runner.txt',
        'schedule.txt',
        'sync.txt',
        'urlhandler.txt',
        'xmlrpc.txt',
        optionflags=flags,
        setUp=setup)
    functional.layer = FunctionalLayer
    return unittest.TestSuite([functional])
