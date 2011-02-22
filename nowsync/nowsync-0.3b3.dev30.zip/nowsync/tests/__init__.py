def suite():
    import unittest
    from nowsync.tests import file
    suite = unittest.TestSuite()
    suite.addTest(file.suite())
    return suite

if __name__ == '__main__':
    import unittest
    #unittest.main(defaultTest='suite')
    unittest.TextTestRunner(verbosity=2).run(suite())