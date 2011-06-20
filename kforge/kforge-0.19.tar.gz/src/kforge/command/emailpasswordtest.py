import unittest

import kforge.testunit
from kforge.command.emailpassword import EmailNewPassword
from kforge.exceptions import *

def suite():
    suites = [
        unittest.makeSuite(TestEmailNewPassword),
    ]
    return unittest.TestSuite(suites)

# todo: Write customer test for integration with SMTP server.

class MockEmailNewPassword(EmailNewPassword):

    def dispatchEmailMessage(self, msgFrom, msgTo, msgSubject, msgBody):
        self.dispatchedMessage = {}
        self.dispatchedMessage['from'] = msgFrom
        self.dispatchedMessage['to'] = msgTo
        self.dispatchedMessage['subject'] = msgSubject
        self.dispatchedMessage['body'] = msgBody
        self.isDispatchedOK = True


class TestEmailNewPassword(kforge.testunit.TestCase):

    def setUp(self):
        self.person = self.registry.persons['levin']
        self.oldPassword = self.person.name
        self.cmd = MockEmailNewPassword(self.person.name)

    def tearDown(self):
        self.person.setPassword(self.oldPassword)
        self.person.save()

    def testExecute(self):
        self.cmd.execute()
        self.failIf(self.person.isPassword(self.oldPassword))
        self.failUnless(self.cmd.dispatchedMessage['from'], self.cmd.dispatchedMessage)
        self.failUnless(self.cmd.dispatchedMessage['to'], self.cmd.dispatchedMessage)
        self.failUnless(self.cmd.dispatchedMessage['subject'], self.cmd.dispatchedMessage)
        self.failUnless(self.cmd.dispatchedMessage['body'], self.cmd.dispatchedMessage)

