import unittest
import doctest
from zope.testing.doctestunit import DocFileSuite
from z3c.zalchemy.testing import placefulSetUp, placefulTearDown

def test_suite():
    return unittest.TestSuite((
        DocFileSuite('keyreference.txt',
                     setUp=placefulSetUp, tearDown=placefulTearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))



if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
