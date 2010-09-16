import os
from tempfile import mkstemp
from ConfigParser import ConfigParser

if __name__ == '__main__':
    import sys
    sys.path.insert(0, '')

from base import TestBase
from base import TEST_URL, TEST_REVS, TEST_MAX_REV
from svnpoller import svnpoller


CONFIG_DATA = '''\
[mail]
smtpserver = localhost
fromaddr = poller@example.com

[PloneTranslations-ja]
url = http://svn.plone.org/svn/collective/PloneTranslations/trunk/i18n/atcontenttypes-ja.po
address = user1@example.com
'''

CONFIG_DATA_SOME_ADDRESS = '''\
[mail]
smtpserver = localhost
fromaddr = poller@example.com

[PloneTranslations-ja]
url = http://svn.plone.org/svn/collective/PloneTranslations/trunk/i18n/atcontenttypes-ja.po
address = user1@example.com, user2@example.com
'''

class TestSvnPoller(TestBase):

    def _make_config(self, data):
        h,fname = mkstemp()
        os.write(h, data)
        os.close(h)
        return fname

    def _remove_config(self, filename):
        if os.path.exists(filename):
            os.unlink(filename)

    def setUp(self):
        super(TestSvnPoller, self).setUp()
        self.config_file = self._make_config(CONFIG_DATA)

    def tearDown(self):
        self._remove_config(self.config_file)
        super(TestSvnPoller, self).tearDown()

    def test_mail_payload(self):
        svnpoller.main(self.config_file, self._stub_sender)

        self.assertEqual(len(TEST_REVS), len(self._sent))
        self.assertEqual('poller@example.com', self._sent[0]['fromaddr'])
        self.assertEqual('user1@example.com', self._sent[0]['toaddrs'][0])
        self.assertEqual(1, len(self._sent[0]['toaddrs']))
        self.assertEqual('localhost', self._sent[0]['smtpserver'])

    def test_plural_mail_address_payload(self):
        self._remove_config(self.config_file) #remove default test ini file
        self.config_file = self._make_config(CONFIG_DATA_SOME_ADDRESS)
        svnpoller.main(self.config_file, self._stub_sender)

        self.assert_(self._sent)
        self.assertEqual('user1@example.com', self._sent[0]['toaddrs'][0])
        self.assertEqual('user2@example.com', self._sent[0]['toaddrs'][1])

    def test_config_update(self):
        svnpoller.main(self.config_file, self._stub_sender)

        conf = ConfigParser()
        conf.read(self.config_file)
        self.assertEqual(str(TEST_REVS[-1]),
                         conf.get('PloneTranslations-ja', 'newest_rev'))

    def test_update_latest_revision(self):
        svnpoller.main(self.config_file, self._stub_sender)
        self.assert_(self._sent)
        self._sent = []

        conf = ConfigParser()
        conf.read(self.config_file)
        rev = conf.get('PloneTranslations-ja', 'newest_rev')
        self.assertEqual(str(TEST_MAX_REV), rev)

        svnpoller.main(self.config_file, self._stub_sender)
        self.assertEqual(0, len(self._sent))


if __name__ == '__main__':
    import unittest
    unittest.main()

