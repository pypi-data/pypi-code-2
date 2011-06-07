import doctest
import unittest
from doctest import DocTestSuite

def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zc.datetimewidget.demo.timezone',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
