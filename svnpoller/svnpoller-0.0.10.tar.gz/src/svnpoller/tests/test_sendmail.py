import base
from svnpoller import sendmail


class TestSendmail(base.TestBase):

    def setUp(self):
        super(TestSendmail, self).setUp()

    def test_send_with_single_string_mail_address(self):
        sendmail.send('from@example.com', 'to1@example.com', 'Subject', 'body', sender=self._storage)
        self.assert_(self._sent)
        self.assertEqual('to1@example.com', self._sent[0]['toaddrs'][0])

    def test_send_with_single_list_mail_address(self):
        sendmail.send('from@example.com', ['to1@example.com'], 'Subject', 'body', sender=self._storage)
        self.assert_(self._sent)
        self.assertEqual('to1@example.com', self._sent[0]['toaddrs'][0])

    def test_send_with_single_tuple_mail_address(self):
        sendmail.send('from@example.com', ('to1@example.com',), 'Subject', 'body', sender=self._storage)
        self.assert_(self._sent)
        self.assertEqual('to1@example.com', self._sent[0]['toaddrs'][0])

    def test_send_with_plural_string_mail_address(self):
        sendmail.send('from@example.com', 'to1@example.com, to2@example.com', 'Subject', 'body', sender=self._storage)
        self.assert_(self._sent)
        self.assertEqual('to1@example.com', self._sent[0]['toaddrs'][0])
        self.assertEqual('to2@example.com', self._sent[0]['toaddrs'][1])

    def test_send_with_single_list_mail_address(self):
        sendmail.send('from@example.com', ['to1@example.com', 'to2@example.com'], 'Subject', 'body', sender=self._storage)
        self.assert_(self._sent)
        self.assertEqual('to1@example.com', self._sent[0]['toaddrs'][0])
        self.assertEqual('to2@example.com', self._sent[0]['toaddrs'][1])

    def test_send_with_single_tuple_mail_address(self):
        sendmail.send('from@example.com', ('to1@example.com', 'to2@example.com'), 'Subject', 'body', sender=self._storage)
        self.assert_(self._sent)
        self.assertEqual('to1@example.com', self._sent[0]['toaddrs'][0])
        self.assertEqual('to2@example.com', self._sent[0]['toaddrs'][1])



