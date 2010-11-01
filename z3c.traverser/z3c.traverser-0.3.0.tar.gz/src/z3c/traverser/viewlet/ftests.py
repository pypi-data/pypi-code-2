import unittest
from zope.app.testing import functional

functional.defineLayer('TestLayer', 'ftesting.zcml', allow_teardown=True)


def test_suite():
    suite = unittest.TestSuite()
    suites = (
        functional.FunctionalDocFileSuite('BROWSER.txt',
                                          ),
        )
    for s in suites:
        s.layer=TestLayer
        suite.addTest(s)
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
