import unittest, os
from optparse import OptionParser
import minimock

FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
TEST_URL = 'http://svn.freia.jp/open/zope2docs/branches'
TEST_REVS = [516,632,655,664,667,668,670]
TEST_MAX_REV = TEST_REVS[-1]

svn_command_parser = OptionParser()
svn_command_parser.add_option('-r', '--revision',
                              action='store', type='string', dest='revision')
svn_command_parser.add_option('-c', '--change',
                              action='store', type='string', dest='change')
svn_command_parser.add_option('', '--xml',
                              action='store_true', default=False, dest='xml')
svn_command_parser.add_option('-v', '--verbose',
                              action='store', type='string', dest='verbose')
svn_command_parser.exit = lambda *args, **kw: None
svn_command_parser.error = lambda *args, **kw: None


def command(cmd):
    #if 'dummy-url' not in cmd:
    #    return command_orig(cmd)

    options, args = svn_command_parser.parse_args(cmd[2:])
    if options.change:
        rev = options.change
    elif options.revision:
        rev = options.revision.replace(':','-')
    else:
        rev = '1-HEAD'

    if 'info' == cmd[1]:
        return 0, open(os.path.join(FIXTURE_DIR, 'info-1.xml')).read(), ''

    elif 'log' == cmd[1]:
        filename = 'log-%s.xml' % rev
        if int(rev.split('-',2)[0]) > TEST_MAX_REV:
            return 1, '<?xml version="1.0"?><log>', ''

        f = os.path.join(FIXTURE_DIR, filename)
        #print f
        return 0, open(f).read(), ''

    elif 'diff' == cmd[1]:
        filename = 'diff-%s.xml' % rev
        f = os.path.join(FIXTURE_DIR, filename)
        #print f
        return 0, open(f).read(), ''

    else:
        raise RuntimeError("'%s' was not supported." % cmd)
        #return svnpoller.svnlog.command(cmd) # call original code.


class TestBase(unittest.TestCase):

    def _storage(self, fromaddr, toaddrs, msg, smtpserver):
        self._sent.append(locals())

    def _stub_sender(self, fromaddr, toaddrs, subject, message_text,
                     smtpserver='localhost', charset='utf-8', sender=None):

        def storage(fromaddr, toaddrs, msg, smtpserver):
            self._sent.append(locals())

        from svnpoller.sendmail import send
        send(fromaddr, toaddrs, subject, message_text,
             smtpserver=smtpserver, charset=charset, sender=storage)

    def _command(self, cmd):
        self._cmd_hist.append(cmd)
        print cmd # print when test failed. (nose functionality)
        return command(cmd)

    def setUp(self):
        self._sent = []
        self._cmd_hist = []
        import svnpoller.svnlog
        minimock.mock('svnpoller.svnlog.command', mock_obj=self._command)

    def tearDown(self):
        minimock.restore()


