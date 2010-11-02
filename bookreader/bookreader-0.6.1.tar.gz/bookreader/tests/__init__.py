import unittest



def test_suite():
    from bookreader.tests import models, fields
    
    suite = unittest.TestSuite()
    suite.addTests(models.test_suite())
    suite.addTests(fields.test_suite())
    return suite

suite=test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(test_suite())
