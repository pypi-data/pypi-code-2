import unittest



def test_suite():
    from bookreader.tests import fields, oai, harvesting
    
    suite = unittest.TestSuite()
    suite.addTests(fields.test_suite())
    suite.addTests(oai.test_suite())
    suite.addTests(harvesting.test_suite())
    
    return suite

suite=test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(test_suite())
