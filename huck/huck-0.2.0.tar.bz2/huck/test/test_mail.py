import os
import unittest
import huck.mail

from cStringIO import StringIO
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

class MessageTestCase(unittest.TestCase):

    FROM='from@example'
    TO='to@example.org'
    SUBJECT='Subject'
    MESSAGE='This is a test message'

    def mail(self, **kwargs):
        return huck.mail.Message(
            kwargs.get('from_addr', self.FROM),
            kwargs.get('to_addrs', self.TO),
            kwargs.get('subject', self.SUBJECT),
            kwargs.get('message', self.MESSAGE),
        )

    def test_basic(self):
        mail = self.mail()
        self.assertEqual(mail.from_addr, self.FROM)
        self.assertEqual(len(mail.to_addrs), 1)
        self.assertEqual(mail.to_addrs[0], self.TO)
        self.assertEqual(mail.subject, self.SUBJECT)
        self.assertTrue(isinstance(mail.message, MIMEText))
        self.assertEqual(mail.message.get_payload(), self.MESSAGE)

    def test_attach(self):
        path = os.path.realpath(__file__)
        name = os.path.basename(path)
        mail = self.mail()
        self.assertEqual(mail.msg, None)
        mail.attach(path)
        self.assertTrue(isinstance(mail.msg, MIMEMultipart))
        self.assertEqual(len(mail.msg.get_payload()), 2)

    def test_render(self):
        mail = self.mail()
        mail_str = mail.render().read()
        self.assertTrue('To: %s' % self.TO in mail_str)
        self.assertTrue('From: %s' % self.FROM in mail_str)
        self.assertTrue('Subject: %s' % self.SUBJECT in mail_str)
        self.assertTrue(self.MESSAGE in mail_str)
