import unittest
from zope.app.testing import functional

functional.defineLayer('TestLayer', 'ftesting.zcml')


def setUp(test):
    """Setup a reasonable environment for the category tests"""
    pass


def tearDown(test):
    pass


def test_suite():
    suite = unittest.TestSuite()
    suites = (
        functional.FunctionalDocFileSuite('README.txt',
                                          setUp=setUp, tearDown=tearDown,
                                         ),
        )
    for s in suites:
        s.layer=TestLayer
        suite.addTest(s)
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
