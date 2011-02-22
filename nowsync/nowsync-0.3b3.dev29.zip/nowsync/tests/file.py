import unittest

from nowsync.models import file

class TestFile(unittest.TestCase):
        
    def test_is_under_dir(self):
        self.assertTrue(file.is_under_dir('a/b/c', 'a'))
        self.assertTrue(file.is_under_dir('a/b/c/../d', 'a'))
        self.assertTrue(file.is_under_dir('/a/b/c', '/a/b/c'))
        self.assertTrue(file.is_under_dir('/a/b/c', '/a/b'))
        self.assertTrue(file.is_under_dir('/a/b/c', '/a'))
        self.assertFalse(file.is_under_dir('a/b/c/../../d', 'a/b'))
        self.assertFalse(file.is_under_dir('a/b/c/../../../d', 'a/b'))
           
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFile))
    return suite
        
if __name__ == '__main__':
    unittest.main(defaultTest='suite')