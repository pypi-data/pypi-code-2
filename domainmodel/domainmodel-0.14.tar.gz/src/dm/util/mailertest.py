import unittest

import dm.utils.mailer

class TestSend(unittest.TestCase):

    def test_send(self):
        to = ['kforge-admin@localhost']
        from_address = to[0]
        subject = 'Testing the kforge email system'
        dm.utils.mailer.send(from_address, to, subject, subject)
        # have to test the result by eye ...

if __name__ == '__main__':
    unittest.main()
