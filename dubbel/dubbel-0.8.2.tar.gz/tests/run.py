
import os
import doctest
import unittest


suite = unittest.TestSuite()
loader = unittest.TestLoader()

#suite.addTest(loader.loadTestsFromModule(testcases))

for root, dirs, files in os.walk('.'):
    for f in files:
        if f.startswith('test_') and f.endswith('.rst'):
            suite.addTest(doctest.DocFileSuite(os.path.join(root, f)))

unittest.TextTestRunner(verbosity=1).run(suite)

