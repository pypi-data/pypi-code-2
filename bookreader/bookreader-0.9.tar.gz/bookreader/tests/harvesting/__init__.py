import unittest



def test_suite():
    from bookreader.tests.harvesting import book, collection
    
    suite = unittest.TestSuite()
    suite.addTests(book.test_suite())
    suite.addTests(collection.test_suite())
    
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(test_suite())
