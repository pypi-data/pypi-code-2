import unittest

import kforge.utils.mailer

class TestSend(unittest.TestCase):
    tags = [ 'cli' ]
    disable = True

    def test_send(self):
        to = ['kforge-admin@localhost']
        from_address = to[0]
        subject = 'Testing the kforge email system'
        kforge.utils.mailer.send(from_address, to, subject, subject)
        # have to test the result by eye ...

if __name__ == '__main__':
    unittest.main()
