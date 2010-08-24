from unittest import TestCase
import datetime
from DateTime import DateTime
from Products.salesforcebaseconnector.utils import DateTime2datetime

class TestSBCUtils(TestCase):
    
    def testDateTime2datetime(self):
        # datetime comes back unscathed
        sample_time = datetime.datetime(2008, 2, 1)
        self.assertEqual(sample_time, DateTime2datetime(sample_time))
        self.assertRaises(ValueError, DateTime2datetime, 'some string')
        self.failUnless(isinstance(DateTime2datetime(DateTime()), datetime.datetime))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSBCUtils))
    return suite

