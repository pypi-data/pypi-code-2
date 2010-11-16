from zope.app.testing import functional

functional.defineLayer('TestLayer', 'ftesting.zcml')

def test_suite():
    suite = functional.FunctionalDocFileSuite(
        'demo/README.txt',
        )
    suite.layer = TestLayer
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
