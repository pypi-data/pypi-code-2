import doctest
import unittest

def additional_tests():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite('linkexchange.config'))
    suite.addTest(doctest.DocTestSuite('linkexchange.db_drivers'))
    suite.addTest(doctest.DocTestSuite('linkexchange.formatters'))
    suite.addTest(doctest.DocTestSuite('linkexchange.platform'))
    suite.addTest(doctest.DocTestSuite('linkexchange.utils'))
    suite.addTest(doctest.DocTestSuite('linkexchange.tests'))
    return suite
