import unittest

from dspace.tests import metadata, repository

  
  
def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(metadata.test_suite())
    suite.addTests(repository.test_suite())
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(test_suite())
